import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Copy the regex patterns from automation.py
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

def has_job_title(text: str) -> bool:
    return any(regex.search(text) for regex in JOB_TITLE_REGEX)

def has_job_context(text: str) -> bool:
    return any(regex.search(text) for regex in JOB_CONTEXT_REGEX)

# Test the genexinfosys/career.php page
url = "https://genexinfosys.com/career.php"
print(f"=== TESTING {url} ===\n")

try:
    html = requests.get(url, headers=HEADERS, timeout=25).text
    soup = BeautifulSoup(html, "html.parser")
    
    print(f"Total links found: {len(soup.find_all('a', href=True))}\n")
    
    for link in soup.find_all("a", href=True):
        text = link.get_text(separator=" ", strip=True)
        href = link["href"].strip()
        if not text or len(text) < 5:
            continue
        
        normalized_text = normalize_text(text)
        normalized_href = href.lower()
        
        title_in_text = has_job_title(normalized_text)
        context_in_text = has_job_context(normalized_text)
        title_in_href = has_job_title(normalized_href)
        context_in_href = has_job_context(normalized_href)
        
        allowed_path = any(
            segment in normalized_href or segment.lstrip("/") in normalized_href
            for segment in JOB_URL_SEGMENTS
        )
        
        would_match = (
            (title_in_text and (context_in_text or allowed_path))
            or (title_in_href and (context_in_text or context_in_href or allowed_path))
        )
        
        # Show interesting links
        if "position" in normalized_href or title_in_text or would_match:
            print(f"TEXT: {text[:80]}")
            print(f"HREF: {href}")
            print(f"  title_in_text={title_in_text}, context_in_text={context_in_text}")
            print(f"  allowed_path={allowed_path}, would_match={would_match}")
            print()
            
except Exception as e:
    print(f"Error: {e}")
