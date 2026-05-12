import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

COLLECTION_NAME = "naija_incidents"

# load once at startup
print("Loading embedding model...")
model = SentenceTransformer("paraphrase-MiniLM-L3-v2")

print("Connecting to Qdrant...")
qdrant = QdrantClient(
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", 6333))
)

print("Connecting to Groq...")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return {"status": "NaijaWatch backend is running"}

@app.post("/ask")
def ask(request: QueryRequest):
    question = request.question.strip()
    if not question:
        return {"error": "Question cannot be empty"}

    # step 1 — embed the question
    query_vector = model.encode(question).tolist()

    # step 2 — search Qdrant for relevant incidents
    results = qdrant.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    limit=5
    ).points

    if not results:
        return {
            "answer": "No relevant incidents found in the knowledge base for your query.",
            "sources": []
        }

    # step 3 — build context from search results
    context_parts = []
    sources = []

    for r in results:
        payload = r.payload
        title = payload.get("title", "")
        body = payload.get("body", "")
        source = payload.get("source", "")
        url = payload.get("url", "")
        scraped_at = payload.get("scraped_at", "")

        context_parts.append(f"INCIDENT: {title}\nDETAILS: {body}\nSOURCE: {source}\nDATE: {scraped_at}")
        sources.append({"title": title, "source": source, "url": url})

    context = "\n\n---\n\n".join(context_parts)

    # step 4 — ask Groq
    prompt = f"""You are a Nigerian security intelligence analyst assistant for NaijaWatch.
Your job is to answer questions about security incidents in Nigeria.

You have two sources of knowledge:
1. LOCAL DATABASE — real-time scraped incidents from Nigerian news sources (use this first)
2. YOUR OWN KNOWLEDGE — your training data about Nigeria (use this as fallback)

STRICT RULES:
- Always check the local database first
- If the local database has relevant incidents, lead with those and label them "📍 Live Feed:"
- If the local database has nothing relevant, STILL answer using your own knowledge and label it "🧠 General Intelligence:"
- Never say "I don't have information" — you always have your training knowledge to fall back on
- Always end with practical safety advice specific to the location asked about
- Always be specific to Nigeria, not generic advice

LOCAL DATABASE (may or may not contain relevant incidents):
{context}

QUESTION: {question}

Respond in this format:

📍 Live Feed: [incidents from local database, or "No live incidents found for this query"]

🧠 General Intelligence: [what you know about security in this area from your training]

⚠️ Safety Advice: [specific, practical advice for someone in that location]

📰 Sources: [list sources used]
"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.2
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": sources
    }