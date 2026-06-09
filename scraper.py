"""
scraper.py — Naukri.com Job Scraper using Playwright
=====================================================
Searches Naukri for jobs using keywords from config.py
and saves results to jobs.csv.

INSTALLATION:
-------------
1. Install dependencies:
   pip install playwright anthropic
   playwright install chromium

2. Edit config.py with your keywords, location, experience range.

3. Run:
   python scraper.py

OUTPUT:
-------
jobs.csv — with columns: title, company, location, experience, description, link, keyword, scraped_at
"""

import csv
import time
import asyncio
from datetime import datetime
from urllib.parse import quote

from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from config import (
    JOB_KEYWORDS,
    LOCATIONS,
    EXPERIENCE_MIN,
    EXPERIENCE_MAX,
    MAX_JOBS_PER_PORTAL,
)

# ── Constants ────────────────────────────────────────────────────────────────

OUTPUT_FILE  = "jobs.csv"
TEST_LIMIT   = 10          # Process only first N jobs per keyword (testing mode)
NAUKRI_BASE  = "https://www.naukri.com"
HEADLESS     = False       # Set True to run browser in background (no visible window)
DELAY        = 1.5         # Seconds to wait between actions (be polite to the server)

CSV_HEADERS = [
    "title", "company", "location", "experience",
    "description", "link", "keyword", "scraped_at"
]

# ── Helpers ──────────────────────────────────────────────────────────────────

def build_naukri_url(keyword: str, location: str, exp_min: int, exp_max: int) -> str:
    """
    Build a Naukri search URL from keyword + location + experience range.
    Example: https://www.naukri.com/senior-data-analyst-jobs-in-hyderabad?experienceX=5%2C9
    """
    # Naukri URL format: /keyword-jobs-in-location
    slug_keyword  = keyword.lower().replace(" ", "-")
    slug_location = location.lower().replace(" ", "-")
    exp_param     = f"{exp_min}%2C{exp_max}"  # URL-encoded "5,9"

    return (
        f"{NAUKRI_BASE}/{slug_keyword}-jobs-in-{slug_location}"
        f"?experienceX={exp_param}&wfhType=0"
    )


def clean_text(text: str) -> str:
    """Strip extra whitespace and newlines from scraped text."""
    if not text:
        return ""
    return " ".join(text.split()).strip()


def save_to_csv(jobs: list[dict], filepath: str) -> None:
    """Append job records to CSV. Creates file with headers if it doesn't exist."""
    file_exists = False
    try:
        with open(filepath, "r") as f:
            file_exists = bool(f.read(1))
    except FileNotFoundError:
        pass

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(jobs)

    print(f"  ✓ Saved {len(jobs)} jobs → {filepath}")


# ── Core Scraper ─────────────────────────────────────────────────────────────

async def scrape_naukri_keyword(page, keyword: str, location: str) -> list[dict]:
    """
    Search Naukri for one keyword+location combination.
    Returns a list of job dicts (up to TEST_LIMIT).
    """
    url = build_naukri_url(keyword, location, EXPERIENCE_MIN, EXPERIENCE_MAX)
    jobs = []

    print(f"\n  Searching: '{keyword}' in '{location}'")
    print(f"  URL: {url}")

    try:
        await page.goto(url, timeout=30_000, wait_until="domcontentloaded")
        await asyncio.sleep(10)

        content = await page.content()

        with open("page_dump.html", "w", encoding="utf-8") as f:
            f.write(content)

        print("HTML dumped to page_dump.html")
        await asyncio.sleep(DELAY)

        # Wait for job cards to appear
        #await page.wait_for_selector("article.jobTuple", timeout=15_000)
        await page.wait_for_selector(".srp-jobtuple-wrapper", timeout=15_000)
        await asyncio.sleep(5)

        #job_cards = await page.query_selector_all("article")
        job_cards = await page.query_selector_all(".srp-jobtuple-wrapper")

        print(f"Found {len(job_cards)} job cards. Processing first {TEST_LIMIT}...")

        #print(f"DEBUG: Found {len(job_cards)} article elements")

    except PlaywrightTimeout:
        print(f"  ⚠ Timeout loading page for '{keyword}' in '{location}'. Skipping.")
        return []
    except Exception as e:
        print(f"  ⚠ Error loading page: {e}. Skipping.")
        return []

    # Grab all job cards on the page
    job_cards = await page.query_selector_all(".srp-jobtuple-wrapper")
    #job_cards = await page.query_selector_all("article")
    print(f"  Found {len(job_cards)} job cards. Processing first {TEST_LIMIT}...")

    for idx, card in enumerate(job_cards[:TEST_LIMIT]):
        try:
            # ── Title ──────────────────────────────────────────────────────
            title_el = await card.query_selector("a.title")
            title    = clean_text(await title_el.inner_text()) if title_el else ""
            link     = await title_el.get_attribute("href")    if title_el else ""

            # ── Company ────────────────────────────────────────────────────
            company_el = await card.query_selector("a.comp-name")
            company    = clean_text(await company_el.inner_text()) if company_el else ""

            # ── Experience ─────────────────────────────────────────────────
            #exp_el  = await card.query_selector("li.experience span.ellipsis")
            exp_el = await card.query_selector(".expwdth")
            exp     = clean_text(await exp_el.inner_text()) if exp_el else ""

            # ── Location ───────────────────────────────────────────────────
            #loc_el  = await card.query_selector("li.location span.ellipsis")
            loc_el = await card.query_selector(".locWdth")

            loc     = clean_text(await loc_el.inner_text()) if loc_el else ""

            # ── Short Description ──────────────────────────────────────────
            #desc_el = await card.query_selector("div.job-description")
            desc_el = await card.query_selector(".job-desc")
            desc    = clean_text(await desc_el.inner_text()) if desc_el else ""

            # Skip blank records
            if not title and not company:
                continue

            job = {
                "title":       title,
                "company":     company,
                "location":    loc,
                "experience":  exp,
                "description": desc[:500],   # cap at 500 chars
                "link":        link if link and link.startswith("http") else NAUKRI_BASE + (link or ""),
                "keyword":     keyword,
                "scraped_at":  datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            jobs.append(job)
            print(f"    [{idx+1:02d}] {title} @ {company} | {loc} | {exp}")

        except Exception as e:
            print(f"    ⚠ Error parsing card {idx+1}: {e}")
            continue

        await asyncio.sleep(0.3)   # small pause between cards

    return jobs


async def run_scraper():
    """
    Main entry point. Iterates over all keywords × locations from config.py
    and scrapes Naukri job listings.
    """
    print("=" * 60)
    print("  Naukri Job Scraper — Starting")
    print(f"  Keywords : {JOB_KEYWORDS}")
    print(f"  Locations: {LOCATIONS}")
    print(f"  Exp range: {EXPERIENCE_MIN}–{EXPERIENCE_MAX} years")
    print(f"  Test mode: first {TEST_LIMIT} jobs per keyword")
    print("=" * 60)

    all_jobs   = []
    seen_links = set()   # Deduplicate across keyword/location combinations

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
        )

        # Single browser context with a realistic user-agent
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
        )
        page = await context.new_page()

        # Hide webdriver flag to reduce bot detection
        await page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        for keyword in JOB_KEYWORDS:
            for location in LOCATIONS:
                jobs = await scrape_naukri_keyword(page, keyword, location)

                # Deduplicate by job link
                new_jobs = []
                for job in jobs:
                    if job["link"] not in seen_links:
                        seen_links.add(job["link"])
                        new_jobs.append(job)

                if new_jobs:
                    save_to_csv(new_jobs, OUTPUT_FILE)
                    all_jobs.extend(new_jobs)

                # Polite delay between searches
                await asyncio.sleep(DELAY * 2)

        await browser.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"  ✅ Scraping complete!")
    print(f"  Total unique jobs saved : {len(all_jobs)}")
    print(f"  Output file             : {OUTPUT_FILE}")
    print("=" * 60)


# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    asyncio.run(run_scraper())
