import schedule
import time
import subprocess
import sys
import os
from datetime import datetime

def run_scraper():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running scraper...")
    result = subprocess.run(
        [sys.executable, "scraper/scraper.py"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(result.stdout)
        print("Scraper finished. Running ingest...")
        run_ingest()
    else:
        print(f"Scraper error: {result.stderr}")

def run_ingest():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ingesting into Qdrant...")
    result = subprocess.run(
        [sys.executable, "scraper/ingest.py"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(result.stdout)
        print("Ingest complete. Knowledge base updated.")
    else:
        print(f"Ingest error: {result.stderr}")

# run immediately on startup
print("NaijaWatch Scheduler started.")
print("Running initial scrape...")
run_scraper()

# then run every night at 2am
schedule.every().day.at("12:00").do(run_scraper)

# also run every 6 hours for fresher data
schedule.every(6).hours.do(run_scraper)

print("Scheduler running. Next scrape in 6 hours.")
print("Press Ctrl+C to stop.\n")

while True:
    schedule.run_pending()
    time.sleep(60)