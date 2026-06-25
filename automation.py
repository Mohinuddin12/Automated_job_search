"""
Daily job watcher for one or more websites.
It checks configured pages for new postings matching keywords.
When a new job appears, it generates a WhatsApp share link and opens WhatsApp Web.

Usage:
  python automation.py        # run once
  python automation.py --loop # keep checking every day

Configure SEARCH_URLS and JOB_KEYWORDS for your target site.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import logging
import re
import time
import webbrowser
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
REPORT_FILE = BASE_DIR / "index.html"
CHECK_INTERVAL_SECONDS = 60 * 60 * 24  # 1 day

# Configure your target pages here.
SEARCH_URLS = [
    "https://datasoft-bd.com",
    "https://brainstation-23.easy.jobs/",
    "https://career.southtechgroup.com/"
    "https://tigerit.com",
    "https://riseuplabs.com/jobs/",
    "https://nascenia.com/category/career/",
    "https://career.cefalo.com/#jobs"
    "https://enosisbd.pinpointhq.com/#js-careers-jobs-block",
    "https://genexinfosys.com/position.php"
]
# Only match vacancy postings for these roles.
JOB_TITLE_PATTERNS = [
    r"\bdevops engineer\b",
    r"\bnetwork engineer\b",
    r"\bSoftware QA Engineer\b",
    r"\bSr. DevOps Engineer\b",
    r"\bit engineer\b",
    r"\bcloud engineer\b",
    r"\bsite reliability engineer\b",
    r"\bsupport engineer\b",
    r"\bsr\.\s+\w+\s+engineer\b",  # Generic: Sr. {something} Engineer
    r"\b\w+\s+engineer\b",  # Generic: {something} Engineer
    r"\b\w+\s+developer\b",  # Generic: {something} Developer
]
JOB_TITLE_REGEX = [re.compile(pattern, re.IGNORECASE) for pattern in JOB_TITLE_PATTERNS]
JOB_CONTEXT_PATTERNS = [
    r"\bcareer\b",
    r"\bcareers\b",
    r"\bjob\b",
    r"\bvacancy\b",
    r"\bvacancies\b",
    r"\bopening\b",
    r"\bopenings\b",
    r"\bposition\b",
    r"\bapply\b",
    r"\bopportunity\b",
    r"\bhiring\b",
    r"\brecruit\b",
    r"\bjoin us\b",
    r"\bjoin our team\b",
    r"\bwork with us\b",
    r"\bjobs\b",
]
JOB_CONTEXT_REGEX = [re.compile(pattern, re.IGNORECASE) for pattern in JOB_CONTEXT_PATTERNS]
JOB_URL_SEGMENTS = [
    "/career",
    "/careers",
    "/job",
    "/jobs",
    "/vacancy",
    "/vacancies",
    "/apply",
    "/opening",
    "/openings",
    "/position",
    "/hiring",
]

# If you want a WhatsApp message pre-addressed to a specific phone,
# use the full international phone number without + or spaces.
# For example: "15551234567" for +1 555 123 4567.
WHATSAPP_PHONE_NUMBER = "+8801785210338"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def format_timestamp(timestamp: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def build_html_report(jobs: list[dict[str, Any]]) -> None:
    rows: list[str] = []
    for job in sorted(jobs, key=lambda job: job.get("first_seen", 0), reverse=True):
        title = html.escape(job["title"])
        url = html.escape(job["url"])
        source = html.escape(job.get("source", ""))
        first_seen = format_timestamp(job.get("first_seen", 0))
        message = f"New job found: {job['title']}\n{job['url']}"
        whatsapp_link = build_whatsapp_url(message)
        rows.append(
            f"""
            <tr>
                <td><a href="{url}" target="_blank">{title}</a></td>
                <td>{source}</td>
                <td>{first_seen}</td>
                <td><a class="button" href="{html.escape(whatsapp_link)}" target="_blank">Send</a></td>
            </tr>
            """
        )

    if not rows:
        rows_html = "<tr><td colspan=\"4\">No jobs found yet.</td></tr>"
    else:
        rows_html = "\n".join(rows)

    html_content = f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <title>Job Search Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 24px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background: #f4f4f4; }}
            .button {{ display: inline-block; padding: 8px 12px; background: #25D366; color: white; text-decoration: none; border-radius: 5px; }}
            .button:hover {{ background: #1ebe5d; }}
        </style>
    </head>
    <body>
        <h1>Job Search Report</h1>
        <p>Open the link in a browser and click "Send" to share the vacancy via WhatsApp.</p>
        <table>
            <thead>
                <tr>
                    <th>Job Title</th>
                    <th>Source Page</th>
                    <th>First Seen</th>
                    <th>Share</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </body>
    </html>
    """

    REPORT_FILE.write_text(html_content, encoding="utf-8")
    logging.info("Wrote HTML report to %s", REPORT_FILE)


def fetch_page(url: str) -> str:
    logging.info("Fetching %s", url)
    response = requests.get(url, headers=HEADERS, timeout=25)
    response.raise_for_status()
    return response.text


def build_job_id(title: str, url: str) -> str:
    digest = hashlib.sha256(f"{title}|{url}".encode("utf-8")).hexdigest()
    return digest


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def has_job_title(text: str) -> bool:
    return any(regex.search(text) for regex in JOB_TITLE_REGEX)


def has_job_context(text: str) -> bool:
    return any(regex.search(text) for regex in JOB_CONTEXT_REGEX)


def is_job_link(text: str, href: str) -> bool:
    normalized_text = normalize_text(text)
    normalized_href = href.lower()

    title_in_text = has_job_title(normalized_text)
    context_in_text = has_job_context(normalized_text)
    title_in_href = has_job_title(normalized_href)
    context_in_href = has_job_context(normalized_href)
    
    # Check for allowed path patterns (handles both absolute and relative URLs)
    allowed_path = any(
        segment in normalized_href or segment.lstrip("/") in normalized_href
        for segment in JOB_URL_SEGMENTS
    )

    return (
        (title_in_text and (context_in_text or allowed_path))
        or (title_in_href and (context_in_text or context_in_href or allowed_path))
    )


def extract_job_posts(html: str, base_url: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[dict[str, str]] = []

    # Extract jobs from links (original logic)
    for link in soup.find_all("a", href=True):
        text = link.get_text(separator=" ", strip=True)
        if not text:
            continue
        href = link["href"].strip()
        if not is_job_link(text, href):
            continue

        full_url = urljoin(base_url, href)
        candidates.append(
            {
                "title": text,
                "url": full_url,
            }
        )

    # Also extract jobs from headings (h1, h2, h3, h4) that match job title patterns
    for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
        text = heading.get_text(separator=" ", strip=True)
        if not text or len(text) < 3:
            continue
        
        normalized_text = normalize_text(text)
        # Check if this heading contains a job title
        if has_job_title(normalized_text):
            candidates.append(
                {
                    "title": text,
                    "url": base_url,
                }
            )

    unique: dict[str, dict[str, str]] = {}
    for job in candidates:
        key = f"{job['title']}|{job['url']}"
        if key not in unique:
            unique[key] = job
    return list(unique.values())


def build_whatsapp_url(message: str) -> str:
    encoded = quote_plus(message)
    if WHATSAPP_PHONE_NUMBER:
        return f"https://api.whatsapp.com/send?phone={WHATSAPP_PHONE_NUMBER}&text={encoded}"
    return f"https://web.whatsapp.com/send?text={encoded}"


def send_whatsapp_notifications(jobs: list[dict[str, str]]) -> None:
    if not jobs:
        return

    lines: list[str] = []
    for index, job in enumerate(jobs, start=1):
        lines.append(f"{index}. {job['title']}\n{job['url']}")

    message = "New jobs found:\n\n" + "\n\n".join(lines)
    whatsapp_url = build_whatsapp_url(message)
    logging.info("Opening WhatsApp link for %d new jobs", len(jobs))
    webbrowser.open(whatsapp_url)


def check_for_new_jobs() -> list[dict[str, Any]]:
    seen_ids: set[str] = set()
    new_jobs: list[dict[str, Any]] = []

    for url in SEARCH_URLS:
        try:
            html = fetch_page(url)
        except Exception as exc:
            logging.error("Failed to fetch %s: %s", url, exc)
            continue

        jobs = extract_job_posts(html, url)
        logging.info("Found %d candidate posts on %s", len(jobs), url)

        for job in jobs:
            job_id = build_job_id(job["title"], job["url"])
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)
            new_jobs.append(
                {
                    "title": job["title"],
                    "url": job["url"],
                    "source": url,
                    "first_seen": int(time.time()),
                }
            )

    # Don't automatically send WhatsApp notifications - let user send manually from HTML report
    # if new_jobs:
    #     send_whatsapp_notifications(new_jobs)

    return new_jobs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Daily website job watcher with WhatsApp link alerts.")
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Keep running and check once per day.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=CHECK_INTERVAL_SECONDS,
        help="Interval between checks in seconds when --loop is enabled.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    while True:
        jobs = check_for_new_jobs()
        if not jobs:
            logging.info("No matching jobs found; skipping report generation.")
        else:
            build_html_report(jobs)

        if not args.loop:
            break

        logging.info("Waiting %d seconds for the next check.", args.interval)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
