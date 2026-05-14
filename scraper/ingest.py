import json
import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "naija_incidents"

def load_incidents(path="data/incidents.json"):
    with open(path, "r") as f:
        return json.load(f)

def setup_collection(client, vector_size):
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        print(f"Created collection: {COLLECTION_NAME}")
    else:
        print(f"Collection already exists: {COLLECTION_NAME}")

def ingest():
    print("Loading incidents...")
    incidents = load_incidents()
    print(f"Found {len(incidents)} incidents")

    print("Loading embedding model...")
    model = SentenceTransformer("intfloat/e5-small-v2")  # small = faster download

    print("Connecting to Qdrant...")
    client = QdrantClient(
    url=os.getenv("QDRANT_HOST"),
    api_key=os.getenv("QDRANT_API_KEY")
    )

    # create collection if needed
    sample_vec = model.encode("test")
    setup_collection(client, len(sample_vec))

    print("Embedding and uploading incidents...")
    points = []
    for i, incident in enumerate(incidents):
        # combine title + body for richer embedding
        text = f"{incident.get('title', '')} {incident.get('body', '')}".strip()
        if not text:
            continue

        vector = model.encode(text).tolist()

        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "title": incident.get("title", ""),
                "body": incident.get("body", "")[:1000],
                "source": incident.get("source", ""),
                "url": incident.get("url", ""),
                "tag": incident.get("tag", ""),
                "scraped_at": incident.get("scraped_at", "")
            }
        ))

        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(incidents)}...")

    # upload in batches
    batch_size = 50
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)

    print(f"\nDone. {len(points)} incidents loaded into Qdrant.")

if __name__ == "__main__":
    ingest()