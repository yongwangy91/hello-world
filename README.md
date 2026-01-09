# Hong Kong Internship Crawler

This is a web application to crawl and display internship opportunities from major financial institutions in Hong Kong (currently **Morgan Stanley** and **Goldman Sachs**).

## Features
- **Web Crawler:** Automatically fetches job listings from career sites using Playwright (handles dynamic content).
- **Dashboard:** Simple web interface to view jobs sorted by date.
- **Visited Tracking:** Links turn dark purple after you click them (browser-based) to help you keep track.
- **Manual Trigger:** "Fetch Latest Jobs" button to start a crawl immediately.

## Prerequisites
- Python 3.8+
- Google Chrome / Chromium (installed via Playwright)

## Installation

1.  **Clone/Update the repository:**
    ```bash
    git pull origin main
    ```

2.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Playwright Browsers:**
    ```bash
    playwright install chromium
    ```

## How to Run

1.  **Start the Server:**
    Run the following command in the project root:
    ```bash
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

2.  **Open the Application:**
    Open your web browser and navigate to:
    ```
    http://localhost:8000
    ```

3.  **Usage:**
    - Click **"Fetch Latest Jobs"** to search for new internships.
    - Refresh the page after a minute to see the new results (grouped by date).
    - Click on a job title to go to the official application page.

## Project Structure
- `main.py`: FastAPI backend application.
- `crawler.py`: Scraper logic using Playwright.
- `database.py`: SQLite database configuration.
- `static/index.html`: Frontend user interface.
- `jobs.db`: Local database file (created automatically).
