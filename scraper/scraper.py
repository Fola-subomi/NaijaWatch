import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

SOURCES = [
    {
        "name": "Punch",
        "url": "https://punchng.com/topics/crime/",
        "tag": "crime"
    },
    {
        "name": "Premium Times",
        "url": "https://www.premiumtimesng.com/news/headlines",
        "tag": "general"
    },
    {
        "name": "Channels TV",
        "url": "https://www.channelstv.com/category/news/",
        "tag": "general"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def scrape_site(source):
    incidents = []
    try:
        res = requests.get(source["url"], headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # grab all article links and titles
        articles = soup.find_all("a", href=True)

        seen = set()
        for a in articles:
            title = a.get_text(strip=True)
            href = a["href"]

            # filter: must be a real article link with a meaningful title
            if len(title) < 30:
                continue
            if href in seen:
                continue
            if not href.startswith("http"):
                continue

            # keyword filter — only security-relevant content
            keywords = [
                "kill", "kidnap", "abduct", "attack", "bandit", "robbery",
                "fraud", "scam", "cyber", "hack", "phish", "ransom",
                "EFCC", "police", "arrest", "victim", "shooting", "bomb",
                "terror", "insurgent", "gang", "theft", "stolen"
            ]
            title_lower = title.lower()
            if not any(kw.lower() in title_lower for kw in keywords):
                continue

            seen.add(href)
            incidents.append({
                "title": title,
                "url": href,
                "source": source["name"],
                "tag": source["tag"],
                "scraped_at": datetime.utcnow().isoformat()
            })

        print(f"  {source['name']}: {len(incidents)} relevant articles found")

    except Exception as e:
        print(f"  ERROR scraping {source['name']}: {e}")

    return incidents


def fetch_article_text(url):
    """Try to get the full article body text."""
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # most Nigerian news sites wrap body in <article> or <div class="entry-content">
        for selector in ["article", "div.entry-content", "div.post-content", "div.article-body"]:
            tag = soup.select_one(selector)
            if tag:
                return tag.get_text(separator=" ", strip=True)[:2000]

        # fallback: grab all paragraphs
        paras = soup.find_all("p")
        return " ".join(p.get_text(strip=True) for p in paras)[:2000]

    except Exception:
        return ""


def run_scraper():
    all_incidents = []

    print("Starting scrape...")
    for source in SOURCES:
        print(f"Scraping {source['name']}...")
        incidents = scrape_site(source)

        # fetch full text for each article
        for item in incidents[:10]:  # limit to 10 per source to be polite
            print(f"    Fetching: {item['title'][:60]}...")
            item["body"] = fetch_article_text(item["url"])

        all_incidents.extend(incidents)

    # save to data folder
    os.makedirs("data", exist_ok=True)
    out_path = "data/incidents.json"
    with open(out_path, "w") as f:
        json.dump(all_incidents, f, indent=2)

    print(f"\nDone. {len(all_incidents)} incidents saved to {out_path}")
    return all_incidents


if __name__ == "__main__":
    run_scraper()