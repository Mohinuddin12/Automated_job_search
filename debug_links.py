import requests
from bs4 import BeautifulSoup

url = 'https://genexinfosys.com/career.php'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=25)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print('=== LINKS CONTAINING DEVOPS or POSITION ===')
    for i, link in enumerate(soup.find_all('a', href=True), 1):
        text = link.get_text(separator=' ', strip=True)
        href = link['href'].strip()
        if text and ('devops' in text.lower() or 'position' in href.lower() or 'sr.' in text.lower()):
            print(f'{i}. TEXT: {text}')
            print(f'   HREF: {href}')
            print()
except Exception as e:
    print(f'Error: {e}')
