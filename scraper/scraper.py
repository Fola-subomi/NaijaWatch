import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

SOURCES = [
    # --- NATIONAL NEWS ---
    {"name": "Punch", "url": "https://punchng.com/topics/crime/", "tag": "crime"},
    {"name": "Punch News", "url": "https://punchng.com/category/news/", "tag": "general"},
    {"name": "Premium Times", "url": "https://www.premiumtimesng.com/news/headlines", "tag": "general"},
    {"name": "Premium Times Crime", "url": "https://www.premiumtimesng.com/news/crime", "tag": "crime"},
    {"name": "Vanguard", "url": "https://www.vanguardngr.com/category/crime/", "tag": "crime"},
    {"name": "Vanguard News", "url": "https://www.vanguardngr.com/category/news/", "tag": "general"},
    {"name": "Channels TV", "url": "https://www.channelstv.com/category/news/", "tag": "general"},
    {"name": "Daily Trust", "url": "https://dailytrust.com/category/news/", "tag": "general"},
    {"name": "The Cable", "url": "https://www.thecable.ng/category/news", "tag": "general"},
    {"name": "Sahara Reporters", "url": "https://saharareporters.com/reports/crime", "tag": "crime"},
    {"name": "ThisDay", "url": "https://www.thisdaylive.com/index.php/category/news/", "tag": "general"},
    {"name": "Leadership", "url": "https://leadership.ng/category/news/", "tag": "general"},
    {"name": "Tribune", "url": "https://tribuneonlineng.com/category/news/", "tag": "general"},
    {"name": "Sun News", "url": "https://www.sunnewsonline.com/category/news/", "tag": "general"},
    {"name": "Blueprint", "url": "https://www.blueprint.ng/category/news/", "tag": "general"},
    {"name": "Guardian Nigeria", "url": "https://guardian.ng/news/", "tag": "general"},
    {"name": "BusinessDay", "url": "https://businessday.ng/news/", "tag": "general"},
    {"name": "NAN", "url": "https://nannews.ng/category/security/", "tag": "crime"},

    # --- NORTH WEST (Kaduna, Kano, Katsina, Kebbi, Sokoto, Zamfara, Jigawa) ---
    {"name": "Daily Trust North West", "url": "https://dailytrust.com/category/northwest/", "tag": "northwest"},
    {"name": "Arewa24 News", "url": "https://arewa24.com/news/", "tag": "northwest"},
    {"name": "Kano Focus", "url": "https://kanofocus.com/category/news/", "tag": "northwest"},
    {"name": "Zamfara Daily", "url": "https://zamfaradaily.com.ng/category/news/", "tag": "northwest"},

    # --- NORTH EAST (Borno, Adamawa, Bauchi, Gombe, Taraba, Yobe) ---
    {"name": "Daily Trust North East", "url": "https://dailytrust.com/category/northeast/", "tag": "northeast"},
    {"name": "Borno Daily", "url": "https://bornodaily.com.ng/category/news/", "tag": "northeast"},
    {"name": "HumAngle", "url": "https://humanglemedia.com/category/news/", "tag": "northeast"},

    # --- NORTH CENTRAL (Abuja FCT, Benue, Kogi, Kwara, Nasarawa, Niger, Plateau) ---
    {"name": "Daily Trust FCT", "url": "https://dailytrust.com/category/fct/", "tag": "northcentral"},
    {"name": "Abuja Reporters", "url": "https://abujaReporters.com/category/news/", "tag": "northcentral"},
    {"name": "Plateau Daily", "url": "https://plateaudaily.com.ng/category/news/", "tag": "northcentral"},
    {"name": "Benue Daily", "url": "https://www.benuedaily.com.ng/category/news/", "tag": "northcentral"},

    # --- SOUTH WEST (Lagos, Ogun, Oyo, Osun, Ondo, Ekiti) ---
    {"name": "Lagos Daily Post", "url": "https://lagospost.ng/category/news/", "tag": "southwest"},
    {"name": "Yoruba Nation News", "url": "https://yorubanation.org/news/", "tag": "southwest"},
    {"name": "Osun Defender", "url": "https://www.osundefender.com/category/news/", "tag": "southwest"},
    {"name": "Ekiti Post", "url": "https://ekitipost.com/category/news/", "tag": "southwest"},
    {"name": "Ondo Talks", "url": "https://ondotalks.com/category/news/", "tag": "southwest"},

    # --- SOUTH SOUTH (Rivers, Delta, Edo, Bayelsa, Akwa Ibom, Cross River) ---
    {"name": "Rivers State News", "url": "https://www.riversstatenews.com/category/news/", "tag": "southsouth"},
    {"name": "The Tide", "url": "https://thetidenewsonline.com/category/news/", "tag": "southsouth"},
    {"name": "Delta Daily Post", "url": "https://deltadailypost.com/category/news/", "tag": "southsouth"},
    {"name": "Edo Daily", "url": "https://edodaily.com.ng/category/news/", "tag": "southsouth"},
    {"name": "Bayelsa Daily", "url": "https://www.bayelsa.news/category/news/", "tag": "southsouth"},

    # --- SOUTH EAST (Anambra, Imo, Enugu, Ebonyi, Abia) ---
    {"name": "Anambra Reporters", "url": "https://anambrareporters.com/category/news/", "tag": "southeast"},
    {"name": "Enugu Daily", "url": "https://www.enugudaily.com.ng/category/news/", "tag": "southeast"},
    {"name": "Imo Daily", "url": "https://imodaily.com.ng/category/news/", "tag": "southeast"},
    {"name": "Eastern Updates", "url": "https://easternupdates.com/category/news/", "tag": "southeast"},

    # --- SECURITY / GOVERNMENT ADVISORIES ---
    {"name": "EFCC", "url": "https://efcc.gov.ng/news/", "tag": "advisory"},
    {"name": "NCC", "url": "https://www.ncc.gov.ng/press-releases", "tag": "advisory"},
    {"name": "Nigeria Police Force", "url": "https://www.npf.gov.ng/news/", "tag": "advisory"},
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
                # violence
                "kill", "killed", "dead", "death", "murder", "kidnap", "abduct",
                "attack", "bandit", "robbery", "robber", "shooting", "gunmen",
                "bomb", "terror", "insurgent", "gang", "theft", "stolen", "armed",
                "massacre", "casualt", "wound", "injur", "hostage", "ransom",
                "cult", "ritual", "lynched", "mob", "clash", "riot", "unrest",
                "invasion", "community", "village", "farmers", "herders",

                # north specific
                "Boko Haram", "ISWAP", "bandits", "cattle rustl", "farmer herder",
                "Zamfara", "Kaduna", "Katsina", "Sokoto", "Kebbi", "Jigawa",
                "Kano", "Borno", "Yobe", "Adamawa", "Gombe", "Bauchi", "Taraba",

                # north central
                "Abuja", "FCT", "Benue", "Kogi", "Kwara", "Nasarawa", "Plateau",
                "Niger State", "Jos", "Makurdi", "Lokoja",

                # south west
                "Lagos", "Ogun", "Oyo", "Osun", "Ondo", "Ekiti", "Ibadan",
                "Abeokuta", "Ile-Ife", "Akure",

                # south south
                "Rivers", "Delta", "Edo", "Bayelsa", "Akwa Ibom", "Cross River",
                "Port Harcourt", "Warri", "Benin City", "Uyo", "Calabar",
                "pipeline", "oil theft", "bunkering", "kidnap oil",

                # south east
                "Anambra", "Imo", "Enugu", "Ebonyi", "Abia",
                "Onitsha", "Owerri", "Enugu city", "IPOB", "ESN", "unknown gunmen",
                "sit-at-home", "Monday lockdown",

                # cyber and fraud
                "fraud", "scam", "cyber", "hack", "phish", "ransom",
                "EFCC", "SIM swap", "BEC", "wire transfer", "ponzi",
                "yahoo boy", "419", "advance fee", "identity theft",
                "data breach", "ATM fraud", "POS fraud",

                # law enforcement
                "police", "arrest", "convict", "prosecut", "sentence", "court",
                "DSS", "military", "soldier", "troops", "operation",
                "NSCDC", "customs", "immigration",
                "EFCC", "NCC", "advisory", "warning", "alert", "security update",
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