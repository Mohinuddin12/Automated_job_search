import requests
from bs4 import BeautifulSoup

url = 'https://genexinfosys.com/position.php'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    response = requests.get(url, headers=headers, timeout=25)
    response.raise_for_status()
    
    # Check if the word "devops" appears anywhere on the page
    if 'devops' in response.text.lower():
        print("✓ 'devops' FOUND on position.php")
        # Find the lines containing devops
        lines = response.text.split('\n')
        for i, line in enumerate(lines):
            if 'devops' in line.lower():
                print(f"   Line {i}: {line.strip()[:150]}")
    else:
        print("✗ 'devops' NOT FOUND on position.php")
        
    # Also check for any engineer positions
    soup = BeautifulSoup(response.text, 'html.parser')
    print("\n=== FIRST 30 JOB POSITIONS FOUND ===")
    
    # Try to extract job titles - they might be in various elements
    text = soup.get_text()
    for word in ['engineer', 'manager', 'developer', 'lead', 'analyst']:
        if word in text.lower():
            print(f"✓ Found '{word}' on the page")
            
except Exception as e:
    print(f'Error: {e}')
