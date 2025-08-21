import requests
from bs4 import BeautifulSoup
import argparse
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO)

VALID_SITES = {
    'wetest': 'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'ip164746': 'https://ip.164746.xyz',
    'cf090227': 'https://cf.090227.xyz',
    'hostmonit': 'https://stock.hostmonit.com/CloudFlareYes'
}

def validate_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(0<=int(p)<=255 for p in parts)

def validate_port(port):
    return port.isdigit() and 1<=int(port)<=65535

def scrape_site(site_key):
    try:
        url = VALID_SITES[site_key]
        logging.info(f"Scraping {site_key} from {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        ips = []
        
        for tr in soup.select('tr'):
            tds = tr.find_all('td')
            if len(tds) >= 2:
                ip = tds[0].text.strip()
                port = tds[1].text.strip()
                if validate_ip(ip) and validate_port(port):
                    ips.append(f"{ip}:{port}")
        
        return ips
    except Exception as e:
        logging.error(f"Error scraping {site_key}: {str(e)}")
        return []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    sources = args.sources.split(',')
    all_ips = []
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(scrape_site, src) for src in sources]
        for future in futures:
            all_ips.extend(future.result())
    
    unique_ips = sorted(list(set(all_ips)), key=lambda x: x.split(':')[0])
    with open(args.output, 'w') as f:
        f.write('\n'.join(unique_ips))

if __name__ == "__main__":
    main()
