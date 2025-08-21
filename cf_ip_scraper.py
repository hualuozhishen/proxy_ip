import requests
import re
import random
import time
from datetime import datetime

TARGETS = [
    "https://www.wetest.vip/page/cloudflare/address_v4.html",
    "https://ip.164746.xyz",
    "https://cf.090227.xyz",
    "https://stock.hostmonit.com/CloudFlareYes"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15"
]

def extract_ips(html):
    """严格匹配IPv4地址"""
    return set(re.findall(r'\b(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b', html))

def fetch_ips(url):
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return extract_ips(response.text) if response.status_code == 200 else set()
    except Exception as e:
        print(f"🚨 抓取失败 {url}: {str(e)}")
        return set()

def main():
    all_ips = set()
    print("="*50)
    
    for i, url in enumerate(TARGETS):
        time.sleep(random.uniform(1, 3))  # 防封IP延迟
        print(f"🔍 [{i+1}/{len(TARGETS)}] 抓取 {url}...")
        ips = fetch_ips(url)
        print(f"✅ 发现 {len(ips)} 个IP")
        all_ips.update(ips)
    
    # 始终写入同一个文件
    output_file = "cf_ips.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# 更新时间: {timestamp}\n")
        f.write(f"# 总IP数量: {len(all_ips)}\n")
        f.writelines(ip + "\n" for ip in sorted(all_ips))
    
    print(f"\n🚀 更新完成！共获取 {len(all_ips)} 个唯一IP → 文件: {output_file}")
    print("="*50)

if __name__ == "__main__":
    main()
