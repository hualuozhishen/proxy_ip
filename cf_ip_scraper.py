import requests
import re
import socket
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup

# 多级重试配置
MAX_RETRIES = 3
REQUEST_TIMEOUT = 15
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15',
    'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36'
]

SOURCES = [
    "https://www.wetest.vip/page/cloudflare/address_v4.html",
    "https://ip.164746.xyz",
    "https://cf.090227.xyz",
    "https://stock.hostmonit.com/CloudFlareYes"
]

def get_with_retry(url):
    """带重试机制的请求函数"""
    for _ in range(MAX_RETRIES):
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            res = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            res.raise_for_status()
            return res.text
        except Exception as e:
            print(f"Retrying {url} | Error: {str(e)}")
            time.sleep(1)
    return None

def get_wetest_ips(url):
    try:
        html = get_with_retry(url)
        if not html: return []
        
        soup = BeautifulSoup(html, 'html.parser')
        return [td.text.strip() for td in soup.select('table td:first-child') 
                if re.match(r'\d+\.\d+\.\d+\.\d+', td.text.strip())]
    except Exception as e:
        print(f"[Wetest Error] {str(e)}")
        return []

def get_text_ips(url):
    try:
        text = get_with_retry(url)
        return re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text) if text else []
    except Exception as e:
        print(f"[Text Source Error] {str(e)}")
        return []

def test_latency(ip, port=443, timeout=2):
    """TCP连接测试延迟（毫秒）"""
    start = time.time()
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return int((time.time() - start) * 1000)
    except:
        return 9999

def main():
    all_ips = []
    print(f"▶ 开始抓取 {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}")
    
    # 多源并行抓取
    for url in SOURCES:
        print(f"▷ 正在处理 {url}")
        if "wetest" in url:
            ips = get_wetest_ips(url)
        else:
            ips = get_text_ips(url)
        print(f"  ✓ 获取 {len(ips)} 个IP")
        all_ips.extend(ips)
    
    # 严格去重
    unique_ips = list(set(filter(None, all_ips)))
    print(f"★ 去重后总IP数: {len(unique_ips)}")
    
    # 延迟测试与分级
    fast_ips = []
    for ip in unique_ips:
        latency = test_latency(ip)
        if latency < 150:
            fast_ips.append((ip, latency))
    
    # 按延迟排序
    fast_ips.sort(key=lambda x: x[1])
    
    # 生成报告
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    report = [
        "# Cloudflare优选IP列表 | 更新时间: {}\n".format(timestamp),
        "# 来源: {}\n".format(", ".join(SOURCES)),
        "# 总IP数量: {}\n".format(len(unique_ips)),
        "\n## 五星推荐 IP (延迟 < 150ms)\n"
    ]
    report += [ip for ip, _ in fast_ips]
    
    # 写入文件
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
    
    print(f"✅ 生成 {len(fast_ips)} 个优选IP")

if __name__ == "__main__":
    main()
