import requests
import re
import socket
import time
from datetime import datetime
from bs4 import BeautifulSoup

SOURCE_CONFIG = [
    {"url": "https://www.wetest.vip/page/cloudflare/address_v4.html", "type": "html"},
    {"url": "https://ip.164746.xyz", "type": "text"}
]

def fetch_html(url):
    try:
        return requests.get(url, timeout=10).text
    except:
        return ""

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    return [td.text.strip() for td in soup.select('table td:first-child') 
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', td.text.strip())]

def parse_text(text):
    return re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)

def test_latency(ip, port=443, timeout=1.5):
    try:
        start = time.time()
        sock = socket.create_connection((ip, port), timeout=timeout)
        sock.close()
        return int((time.time() - start) * 1000)
    except:
        return 9999

if __name__ == "__main__":
    all_ips = []
    for source in SOURCE_CONFIG:
        content = fetch_html(source["url"])
        ips = parse_html(content) if source["type"] == "html" else parse_text(content)
        all_ips.extend(ips)
    
    unique_ips = list(set(all_ips))
    fast_ips = [ip for ip in unique_ips[:50] if test_latency(ip) < 150]
    
    with open('README.md', 'w') as f:
        f.write(f"# Cloudflare优选IP列表 | 更新时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("## 五星推荐 IP (延迟 < 150ms)\n```\n")
        f.write("\n".join(fast_ips))
        f.write("\n```")
