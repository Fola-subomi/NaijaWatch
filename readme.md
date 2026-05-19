# 🛡️ NaijaWatch

> A full-stack RAG intelligence platform for monitoring physical and digital security threats across Nigeria.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![Qdrant](https://img.shields.io/badge/Qdrant-Cloud-purple)
![Groq](https://img.shields.io/badge/Groq-Llama3.1-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What is NaijaWatch?

NaijaWatch is a neighbourhood-watch style intelligence platform that lets anyone in Nigeria ask plain questions about security threats — kidnappings, armed attacks, cybercrime, fraud — and get grounded, cited answers pulled from real Nigerian news sources and government advisories.

Think of it as a searchable, AI-powered community safety bulletin board for Nigeria.

**Live site:** [fola-subomi.github.io/NaijaWatch](https://fola-subomi.github.io/NaijaWatch)  
**API:** [naijawatch-production.up.railway.app](https://naijawatch-production.up.railway.app)  
**API Docs:** [naijawatch-production.up.railway.app/docs](https://naijawatch-production.up.railway.app/docs)

---

## Features

- **Natural language queries** — Ask "What attacks happened in Lagos this week?" and get a cited, structured answer
- **Live incident feed** — Real-time scraping from 40+ Nigerian news sources and government advisories
- **Breaking news ticker** — Vertically scrolling live incident feed
- **Zone-based filtering** — Search by geopolitical zone (North West, South East, etc.)
- **Threat type filtering** — Kidnappings, armed attacks, cybercrime, financial fraud, insurgency
- **Groq fallback** — When the local database lacks data, Groq's training knowledge fills the gap
- **Automated ingestion** — GitHub Actions runs the scraper every 6 hours automatically

---

## Coverage

### Physical Security
- Armed bandit attacks
- Kidnappings and abductions
- Community invasions
- Insurgency (Boko Haram, ISWAP)
- Farmer-herder clashes

### Digital Security
- Business Email Compromise (BEC)
- SIM-swap fraud
- Phishing campaigns
- Ransomware
- EFCC cybercrime arrests

### Data Sources
- Punch, Premium Times, Vanguard, Daily Trust, Channels TV
- The Cable, Sahara Reporters, Tribune, Guardian Nigeria
- EFCC press releases
- ngCERT bulletins
- NCC advisories
- Nigeria Police Force statements
- Regional outlets across all 6 geopolitical zones

---

## Architecture

```
Nigerian News Sources + Government Advisories
              ↓
     Scraper (BeautifulSoup)
              ↓
    Sentence Transformer Embeddings
              ↓
       Qdrant Vector Database
              ↓
    FastAPI RAG Backend + Groq LLM
              ↓
        HTML/JS Frontend
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| Backend | FastAPI, Uvicorn |
| AI/LLM | Groq (Llama 3.1 8B) |
| Embeddings | Sentence Transformers (paraphrase-MiniLM-L3-v2) |
| Vector DB | Qdrant Cloud |
| Scraping | BeautifulSoup, Requests |
| Frontend | HTML, CSS, JavaScript |
| Backend Hosting | Railway |
| Frontend Hosting | GitHub Pages |
| Automation | GitHub Actions |
| Version Control | Git, GitHub |

---

## Project Structure

```
NaijaWatch/
├── backend/
│   └── main.py              # FastAPI app — /ask and /recent endpoints
├── scraper/
│   ├── scraper.py           # Scrapes 40+ Nigerian news sources
│   ├── ingest.py            # Embeds and uploads incidents to Qdrant
│   └── scheduler.py         # Local scheduler (runs every 6 hours)
├── .github/
│   └── workflows/
│       └── scraper.yml      # GitHub Actions automation
├── index.html               # Frontend interface
├── requirements.txt
├── runtime.txt
└── .env                     # API keys (not committed)
```

---

## Getting Started

### Prerequisites
- Python 3.11
- Docker Desktop (for local Qdrant)
- A [Groq API key](https://console.groq.com)
- A [Qdrant Cloud](https://cloud.qdrant.io) account

### Installation

```bash
# Clone the repo
git clone https://github.com/Fola-subomi/NaijaWatch.git
cd NaijaWatch

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root folder:

```
GROQ_API_KEY=gsk_your_key_here
QDRANT_HOST=https://xxxx-xxxx.aws.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_key_here
```

### Run Locally

```bash
# 1. Scrape incidents
python scraper/scraper.py

# 2. Ingest into Qdrant
python scraper/ingest.py

# 3. Start the backend
uvicorn backend.main:app --reload

# 4. Open frontend/index.html in your browser
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/ask` | Ask a natural language question |
| GET | `/recent` | Get 10 most recent incidents |

### Example Request

```bash
curl -X POST https://naijawatch-production.up.railway.app/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What kidnappings happened in Kaduna recently?"}'
```

### Example Response

```json
{
  "answer": "📍 Live Feed: ...\n🧠 General Intelligence: ...\n⚠️ Safety Advice: ...",
  "sources": [
    {
      "title": "Travellers abducted on Kaduna highway",
      "source": "Channels TV",
      "url": "https://..."
    }
  ]
}
```

---

## Automated Scraping

The scraper runs automatically every 6 hours via GitHub Actions. To trigger it manually:

1. Go to your GitHub repo
2. Click **Actions** tab
3. Click **NaijaWatch Scraper**
4. Click **Run workflow**

Required GitHub secrets:
- `QDRANT_HOST`
- `QDRANT_API_KEY`

---

## Deployment

### Backend — Railway
1. Connect GitHub repo to [railway.app](https://railway.app)
2. Add environment variables in Railway dashboard
3. Set start command: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Frontend — GitHub Pages
1. Go to repo Settings → Pages
2. Deploy from branch `main`, folder `/ (root)`

### Database — Qdrant Cloud
1. Create free cluster at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Copy URL and API key to `.env`

---

## Roadmap

- [ ] WhatsApp Bot integration
- [ ] State-level filtering
- [ ] User-submitted incident reports
- [ ] Email/SMS alerts for subscribed zones
- [ ] STIX 2.1 structured output for SIEM integration
- [ ] Dark web monitoring

---

## Contributing

Pull requests are welcome. For major changes please open an issue first.

---

## Disclaimer

NaijaWatch aggregates publicly available information for community safety awareness. All answers are grounded in cited sources. Verify critical information before acting.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
