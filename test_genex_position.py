import sys
sys.path.insert(0, '.')
from automation import check_for_new_jobs, build_html_report

# Just test the genexinfosys URL
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, quote_plus

url = 'https://genexinfosys.com/position.php'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"Testing: {url}\n")

try:
    response = requests.get(url, headers=headers, timeout=25)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for all links with "devops" in text or href
    count = 0
    for link in soup.find_all('a', href=True):
        text = link.get_text(separator=' ', strip=True)
        href = link['href'].strip()
        if 'devops' in text.lower() or 'devops' in href.lower():
            count += 1
            print(f"{count}. TEXT: {text[:80]}")
            print(f"   HREF: {href[:80]}")
            print()
            
    if count == 0:
        print("No DevOps links found on this page via BeautifulSoup")
    
    # Now test with the automation.py's logic
    print("\n" + "="*60)
    print("Testing with automation.py extraction logic:")
    print("="*60 + "\n")
    
    from automation import extract_job_posts
    jobs = extract_job_posts(response.text, url)
    print(f"Total jobs extracted: {len(jobs)}\n")
    for job in jobs[:5]:
        print(f"- {job['title']}")
        print(f"  {job['url']}\n")
    
    if any('devops' in job['title'].lower() for job in jobs):
        print("\n✓ SUCCESS: Sr. DevOps Engineer job WAS extracted!")
    else:
        print("\n✗ FAILED: Sr. DevOps Engineer job was NOT extracted")
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
