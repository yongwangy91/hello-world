import logging
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session
from database import SessionLocal, Job
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_job(db: Session, title: str, company: str, link: str, location: str, date_posted: str):
    # Check if job exists
    existing_job = db.query(Job).filter(Job.link == link).first()
    if existing_job:
        # logger.info(f"Job already exists: {title}")
        return

    new_job = Job(
        title=title,
        company=company,
        link=link,
        location=location,
        date_posted=date_posted,
        crawled_at=datetime.utcnow()
    )
    db.add(new_job)
    db.commit()
    logger.info(f"Saved new job: {title}")

def crawl_morgan_stanley(db: Session):
    logger.info("Starting Morgan Stanley crawl...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Morgan Stanley Job Search URL with filters
        # Using the base search URL and will try to interact with filters or use a direct query string if possible.
        # Based on previous research, they use a dynamic loading system.
        # Let's try to hit the main search page and use selectors.

        # A more direct URL approach if possible:
        # URL found in search: https://morganstanley.tal.net/vx/lang-en-GB/mobile-0/brand-2/xf-a77383610214/candidate/jobboard/vacancy/1/adv/
        # This seems to be the iframe source or main job board.
        # Let's use the main career search page.
        url = "https://morganstanley.tal.net/vx/lang-en-GB/mobile-0/brand-2/xf-a77383610214/candidate/jobboard/vacancy/1/adv/"
        page.goto(url)
        page.wait_for_timeout(5000)

        # We need to filter for "Hong Kong" and "Intern".
        # Since interacting with complex JS filters can be flaky, I'll try to extract everything and filter in Python first
        # OR try to click the filters if they are simple.
        # Looking at the text view, there are checkboxes.

        # Attempt to click "Asia (excluding Japan)" or similar if visible, or "Hong Kong".
        # Since I can't see the exact DOM ID easily without trial, I will fetch all jobs and filter by text content if the list is manageable,
        # or rely on the fact that I can't easily filter via URL parameters on this specific system without reverse engineering the hash.

        # Wait - I can search by keyword "Hong Kong Internship" or similar?
        # Let's try to find the "Filter by keywords" input.

        try:
            # Type "Hong Kong" in keyword filter
            # Based on text view: "Filter on keywords ____________________ Go"
            # The input probably has a name or id.
            # I'll search for an input field.
            page.fill('input[type="text"]', "Hong Kong") # This is a guess, might need refinement
            page.keyboard.press("Enter")
            page.wait_for_timeout(5000)
        except Exception as e:
            logger.error(f"Could not filter by keyword: {e}")

        # Now extract jobs
        # Selectors need to be generic enough.
        # Usually jobs are in `tr` or `li` or `div` with a specific class.
        # Based on previous text output: "Title City" headers suggest a table or grid.

        job_links = page.locator("a").all()

        for link in job_links:
            try:
                text = link.inner_text().strip()
                href = link.get_attribute("href")

                # Filter for relevant jobs
                if "Intern" in text and "Hong Kong" in text: # Basic text filter
                     # We need to reconstruct full URL if relative
                    if href and not href.startswith("http"):
                        href = "https://morganstanley.tal.net" + href

                    save_job(db, text, "Morgan Stanley", href, "Hong Kong", datetime.now().strftime("%Y-%m-%d"))

                # Also check parent element if location is separate
                # This simplistic loop might miss if text is split.
                # Let's look for row elements.
            except:
                continue

        # Better approach: Iterate over rows
        # The text view showed "Title City".
        # Let's try to find table rows.
        rows = page.locator("tr").all()
        for row in rows:
            try:
                text = row.inner_text()
                if "Hong Kong" in text and ("Intern" in text or "Analyst" in text):
                    # Extract link
                    link_el = row.locator("a").first
                    title = link_el.inner_text().strip()
                    href = link_el.get_attribute("href")
                    if href and not href.startswith("http"):
                        href = "https://morganstanley.tal.net" + href

                    save_job(db, title, "Morgan Stanley", href, "Hong Kong", datetime.now().strftime("%Y-%m-%d"))
            except:
                continue

        browser.close()
    logger.info("Morgan Stanley crawl finished.")

def crawl_goldman_sachs(db: Session):
    logger.info("Starting Goldman Sachs crawl...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Direct URL found in research:
        # https://higher.gs.com/campus?EXPERIENCE_LEVEL=Summer%20Analyst&LOCATION=Hong%20Kong
        # Note: Spaces need encoding or Playwright handles it.
        url = "https://higher.gs.com/campus?EXPERIENCE_LEVEL=Summer%20Analyst&LOCATION=Hong%20Kong"
        page.goto(url)
        page.wait_for_timeout(5000)

        # GS site usually uses cards or a list.
        # Let's grab all links that look like job posts.

        # Wait for some content to load
        try:
            page.wait_for_selector("a", timeout=10000)
        except:
            logger.warning("Timeout waiting for GS content.")

        links = page.locator("a").all()
        for link in links:
            try:
                title = link.inner_text().strip()
                href = link.get_attribute("href")

                # GS titles usually look like "2025 Summer Analyst..."
                if title and "Summer Analyst" in title:
                    if href and not href.startswith("http"):
                        href = "https://higher.gs.com" + href

                    save_job(db, title, "Goldman Sachs", href, "Hong Kong", datetime.now().strftime("%Y-%m-%d"))
            except:
                continue

        browser.close()
    logger.info("Goldman Sachs crawl finished.")

def run_crawlers():
    db = SessionLocal()
    try:
        crawl_morgan_stanley(db)
        crawl_goldman_sachs(db)
    finally:
        db.close()

if __name__ == "__main__":
    # For testing
    from database import init_db
    init_db() # Ensure DB exists
    run_crawlers()
