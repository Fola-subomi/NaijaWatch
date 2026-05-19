# Naija Watch 🛡️
### Nigeria's Community Digital & Physical Safety Desk

A neighbourhood-watch style safety intelligence platform for Nigerians. People can ask plain-language questions about scams, fraud, suspicious messages, and physical security incidents — and get direct, actionable answers in plain English or Pidgin. No jargon. No institutions. Just a trusted community desk.

---

## What it does

Naija Watch has three tabs:

**Digital Scams** — Ask anything about fraud targeting Nigerians: OTP harvest calls, fake POS receipts, WhatsApp job scams, phishing links, BVN requests. The AI answers with a clear verdict (scam / legit / caution), explains how it works, and gives numbered steps to take right now.

**Physical Safety** — Curated incident cards from verified Nigerian news outlets covering kidnappings, bandit attacks, road safety warnings, and EFCC operations. Click any card to get a plain-language safety briefing.

**Live News** — Fetches real-time security incidents from Punch, Vanguard, Channels TV, Premium Times, and official sources (EFCC, ngCERT) using web search. Filter by incident type: kidnappings, fraud/EFCC, armed attacks.

Users can also submit scam reports through the "Report a scam" form — anonymous, with channel, state, phone number or link. Every report grows the community knowledge base.

---

## Project structure

```
naija-watch/
├── naija-watch.html       # Full single-file MVP — UI + API logic
├── README.md              # This file
```

The MVP is intentionally a single HTML file so it can be opened directly in a browser, deployed to any static host (Netlify, Vercel, GitHub Pages), or sent to testers without setup.

---

## How it works technically

### Query flow — Digital scams

```
User question
     │
     ▼
Claude API (claude-sonnet-4-20250514)
System prompt: Nigerian scam adviser, plain English,
               structured output (VERDICT / HOW IT WORKS / WHAT TO DO / SOURCES)
     │
     ▼
Rendered answer with verdict badge + numbered steps + source pills
```

### Query flow — Physical safety / Live news

```
User question or "Fetch news" button
     │
     ▼
Claude API + web_search tool enabled
Searches: Punch, Vanguard, Channels TV, Premium Times, EFCC, ngCERT
     │
     ▼
Structured news cards (TITLE / SOURCE / TIME / LOCATION / SUMMARY / RISK / TAGS)
     │
     ▼
Rendered incident cards with risk badge + click-to-ask
```

### Smart query routing

Physical safety keywords (`kidnap`, `attack`, `bandit`, `travel`, `road`, `shoot`, `abduct`) automatically route the query to the physical safety prompt with web search enabled. Everything else routes to the digital scam prompt.

---

## System prompts

Three distinct prompts are used depending on context:

**SYS_DIGITAL** — For scam and fraud questions. Instructs the model to give a clear verdict, explain in plain English or Pidgin, reference real Nigerian banks and platforms, and cite sources like EFCC advisories or community reports.

**SYS_PHYSICAL** — For security incident questions. Instructs the model to use only verified news facts, state a risk level, identify affected locations, and provide 2–3 practical safety actions. Explicitly avoids speculation and graphic detail.

**SYS_NEWS** — For fetching the live news feed. Instructs the model to search and return exactly 4 stories in a strict structured format (TITLE / SOURCE / TIME / LOCATION / SUMMARY / RISK / TAGS) separated by `---` for reliable parsing.

---

## News sources monitored

| Outlet | Focus |
|---|---|
| Punch Nigeria | Crime, security, EFCC |
| Vanguard News | Crime, north-west incidents |
| Channels TV | Breaking security news |
| Premium Times | Investigations, EFCC |
| ThisDay Live | Security, north-east |
| EFCC Nigeria (official) | Fraud arrests |
| ngCERT | Cyber incident alerts |

---

## Running locally

No build step. No dependencies. Just open the file.

```bash
# Option 1 — open directly
open naija-watch.html

# Option 2 — serve locally (avoids any browser CORS restrictions)
npx serve .
# or
python -m http.server 8080
```

The Anthropic API key is handled by the Claude.ai artifact environment. To run this outside Claude.ai, add your API key to the fetch headers:

```javascript
headers: {
  'Content-Type': 'application/json',
  'x-api-key': 'YOUR_ANTHROPIC_API_KEY',
  'anthropic-version': '2023-06-01',
  'anthropic-dangerous-direct-browser-calls': 'true'
}
```

> ⚠️ Never expose your API key in a public-facing HTML file. For production, proxy all API calls through a backend server.

---

## Deploying to production

The MVP HTML file works as-is for testing and demos. For a real deployment, the recommended path is:

**Step 1 — Add a FastAPI backend**

Move API calls server-side to protect your Anthropic key and add rate limiting.

```python
# main.py
from fastapi import FastAPI
from anthropic import Anthropic

app = FastAPI()
client = Anthropic()

@app.post("/ask")
async def ask(payload: dict):
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        system=payload["system"],
        messages=[{"role": "user", "content": payload["question"]}]
    )
    return {"answer": response.content[0].text}
```

**Step 2 — Add a database for community reports**

Use Supabase (free tier) to persist submitted scam reports. These become your growing community knowledge base.

```sql
create table reports (
  id uuid primary key default gen_random_uuid(),
  description text,
  channel text,
  state text,
  contact_used text,
  created_at timestamptz default now()
);
```

**Step 3 — Add RSS ingestion (the data flywheel)**

Run a scheduled Python job to ingest Nigerian news outlets into a vector database. This is the path from "Claude + web search" to a true RAG system grounded in your own curated corpus.

```python
import feedparser
from qdrant_client import QdrantClient

FEEDS = [
    "https://punchng.com/feed/",
    "https://www.vanguardngr.com/feed/",
    "https://www.channelstv.com/feed/",
    "https://www.premiumtimesng.com/feed/"
]

SECURITY_KEYWORDS = [
    "kidnap", "abduct", "bandit", "attack", "robbery", "EFCC",
    "fraud", "scam", "phishing", "cybercrime", "ransom", "shoot",
    "insurgent", "bomb", "terror", "herdsmen", "clash"
]

def is_security_related(entry):
    text = (entry.get("title", "") + entry.get("summary", "")).lower()
    return any(k in text for k in SECURITY_KEYWORDS)

def ingest_feeds():
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if is_security_related(entry):
                # chunk, embed, upsert to Qdrant
                pass
```

**Step 4 — WhatsApp Business API**

Once the web version works well, add a WhatsApp integration. The same FastAPI backend handles both channels — just a different input/output adapter.

```
WhatsApp message → Twilio webhook → FastAPI → Anthropic API → Response → WhatsApp
```

Recommended provider for Nigeria: **Twilio** or **Infobip** (both have Nigerian presence). Apply for WhatsApp Business API access with your working web demo as proof of concept.

---

## Roadmap

**Now (MVP)**
- Single HTML file, fully functional
- AI-powered scam Q&A (digital)
- Physical safety Q&A with web search
- Live news feed from Nigerian outlets
- Community scam report form
- Feedback buttons (thumbs up/down) on every answer

**Next (v2 — backend)**
- FastAPI proxy (secure API key)
- Supabase DB for community reports
- RSS ingestion pipeline → Qdrant vector store
- RAG retrieval grounded in community + news corpus
- User accounts (optional, lightweight)

**Later (v3 — distribution)**
- WhatsApp Business API integration
- Pidgin language detection and response
- State-level filtering and alerts
- Weekly community safety digest (email/WhatsApp)
- MSSP or community org partnership for data sharing

---

## Design decisions

**Why a single HTML file for MVP?** Speed of iteration. No build pipeline, no deployment friction, no dependency management. The architecture is correct from day one — it just needs a backend wrapper when ready to scale.

**Why Claude instead of a fine-tuned model?** Nigerian scam patterns change weekly. A fine-tuned model would require constant retraining. Claude with a well-crafted system prompt adapts to new patterns through the knowledge base without retraining.

**Why web-first before WhatsApp?** WhatsApp Business API approval takes 1–3 weeks and can be rejected. The web app is the development environment and the proof-of-concept that gets the approval.

**Why plain English, not security jargon?** The user is a market trader, a student, a church treasurer — not a SOC analyst. Every answer is written for someone who has never heard the word "phishing."

---

## Editorial guidelines

When adding incident cards or scam reports to the knowledge base, follow these principles:

- Source only from verified Nigerian outlets or official bodies (EFCC, NCC, ngCERT, CBN)
- No graphic details — describe what happened factually, not graphically
- Frame everything as safety awareness: "what does this mean for you" not "here are the gory details"
- Never publish unverified social media rumours as fact
- For physical incidents, always include a practical safety action — awareness without action is anxiety, not help

---

## Contributing

This project is intentionally community-first. If you want to contribute:

- Submit real scam reports through the form (they become training data)
- Suggest new scam types or incident categories via issues
- Improve the system prompts for more accurate verdicts
- Add support for Yoruba, Hausa, or Igbo queries
- Help with the RSS ingestion pipeline

---

## License

MIT — build on it, fork it, deploy it. If you use it to protect Nigerians, that's the point.

---

*Built for the neighbourhood. Not for institutions.*