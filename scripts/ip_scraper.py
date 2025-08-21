import requests
from bs4 import BeautifulSoup
import argparse
from concurrent.futures import ThreadPoolExecutor

def validate_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(0<=int(p)<=255 for p in parts)

def validate_port(port):
    return port.isdigit() and 1<=int(port)<=65535

def scrape_site(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; IPScraper/1.0)',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        ips = []
        
        # 通用解析逻辑（根据实际页面调整）
        for tr in soup.select('tr'):
            tds = tr.find_all('td')
            if len(tds) >= 2:
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                if validate_ip(ip) and validate_port(port):
                    ips.append(f"{ip}:{port}")
        
        return ips
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    sources = args.sources.split(',')
    all_ips = []
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(scrape_site, sources)
    
    unique_ips = list(set([ip for sublist in results for ip in sublist]))
    with open(args.output, 'w') as f:
        f.write('\n'.join(sorted(unique_ips)))
