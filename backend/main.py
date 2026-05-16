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
    url=os.getenv("QDRANT_HOST"),
    api_key=os.getenv("QDRANT_API_KEY")
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
    try:
        question = request.question.strip()
        if not question:
            return {"error": "Question cannot be empty"}

        # embed the question
        query_vector = model.encode(question).tolist()

        # search Qdrant
        results = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=5
        ).points

        sources = []
        context_parts = []

        for r in results:
            payload = r.payload
            title = payload.get("title", "")
            body = payload.get("body", "")
            source = payload.get("source", "")
            url = payload.get("url", "")
            scraped_at = payload.get("scraped_at", "")
            context_parts.append(
                f"INCIDENT: {title}\nDETAILS: {body}\nSOURCE: {source}\nDATE: {scraped_at}"
            )
            sources.append({"title": title, "source": source, "url": url})

        context = "\n\n---\n\n".join(context_parts) if context_parts else "No matching incidents in local database."

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

LOCAL DATABASE:
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

        return {
            "answer": response.choices[0].message.content,
            "sources": sources
        }

    except Exception as e:
        return {"error": str(e), "answer": f"Backend error: {str(e)}", "sources": []}
    
@app.get("/recent")
def recent():
    try:
        results, _ = qdrant.scroll(
            collection_name=COLLECTION_NAME,
            limit=10,
            with_payload=True,
            with_vectors=False
        )
        news = []
        for r in results:
            p = r.payload
            tag = p.get("tag", "general")
            type_map = {
                "crime":       ("Armed Attack",  "#FAECE7", "#712B13"),
                "kidnap":      ("Kidnapping",    "#FBEAF0", "#72243E"),
                "cyber":       ("Cybercrime",    "#E6F1FB", "#0C447C"),
                "fraud":       ("Fraud",         "#FAEEDA", "#633806"),
                "advisory":    ("Advisory",      "#E8F5E9", "#1a472a"),
                "northeast":   ("North East",    "#FAECE7", "#712B13"),
                "northwest":   ("North West",    "#FAECE7", "#712B13"),
                "northcentral":("North Central", "#FAECE7", "#712B13"),
                "southwest":   ("South West",    "#E6F1FB", "#0C447C"),
                "southsouth":  ("South South",   "#FAEEDA", "#633806"),
                "southeast":   ("South East",    "#FBEAF0", "#72243E"),
                "general":     ("Incident",      "#F5F5F0", "#555555"),
            }
            label, bg, color = type_map.get(tag, type_map["general"])
            title = p.get("title", "")
            body = p.get("body", "")
            scraped_at = p.get("scraped_at", "")
            time_label = scraped_at[:10] if scraped_at else "Recent"
            news.append({
                "type": tag,
                "typeLabel": label,
                "typeColor": bg,
                "typeText": color,
                "title": title,
                "body": body[:300] + "..." if len(body) > 300 else body,
                "source": p.get("source", ""),
                "url": p.get("url", ""),
                "location": "Nigeria",
                "time": time_label,
                "query": title
            })
        return {"incidents": news}
    except Exception as e:
        return {"incidents": [], "error": str(e)}