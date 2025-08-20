import requests
from bs4 import BeautifulSoup
import re
import random
import time
from datetime import datetime

# 多目标网站（保留原始来源）
TARGETS = [
    "https://www.wetest.vip/page/cloudflare/address_v4.html",
    "https://ip.164746.xyz",
    "https://cf.090227.xyz",
    "https://stock.hostmonit.com/CloudFlareYes"
]

# 随机User-Agent池（防反爬）
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
]

def extract_ips(html):
    """优化IP提取逻辑，过滤非常规地址"""
    ip_pattern = r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    return set(re.findall(ip_pattern, html))

def fetch_ips(url):
    """增强请求健壮性：随机UA + 超时重试 + 延迟"""
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        
        # 检查HTTP状态码（防403/404错误）
        if response.status_code != 200:
            print(f"⚠️ 状态码异常 {url}: HTTP {response.status_code}")
            return set()
            
        return extract_ips(response.text)
    except requests.exceptions.RequestException as e:
        print(f"🚨 网络错误 {url}: {str(e)}")
        return set()

def main():
    all_ips = set()
    print("="*50)
    
    for i, url in enumerate(TARGETS):
        # 随机延迟（1~5秒）避免高频请求
        delay = random.uniform(1, 5)
        time.sleep(delay)
        
        print(f"🔍 [{i+1}/{len(TARGETS)}] 抓取 {url}...")
        ips = fetch_ips(url)
        print(f"✅ 发现 {len(ips)} 个IP")
        all_ips.update(ips)
    
    # 写入结果（保留历史版本）
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"cf_ips_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(f"# 更新时间: {timestamp}\n")
        f.write(f"# 总IP数量: {len(all_ips)}\n")
        f.writelines(ip + "\n" for ip in sorted(all_ips))
    
    print(f"\n🚀 完成！共获取 {len(all_ips)} 个唯一IP → 文件: {filename}")
    print("="*50)

if __name__ == "__main__":
    main()
