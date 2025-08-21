import os
import requests
import re
import random
import time
from datetime import datetime

# 目标网站列表
TARGETS = [
    "https://www.wetest.vip/page/cloudflare/address_v4.html",
    "https://ip.164746.xyz",
    "https://cf.090227.xyz",
    "https://stock.hostmonit.com/CloudFlareYes"
]

# 增强型User-Agent池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
]

# 严格IP匹配正则
IP_PATTERN = r'\b(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b'

def extract_ips(html):
    """从HTML中提取有效IPv4地址"""
    return set(re.findall(IP_PATTERN, html))

def fetch_with_retry(url, retries=3):
    """带重试机制的请求函数"""
    for attempt in range(retries):
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            if attempt < retries - 1:
                delay = 2 ** attempt  # 指数退避
                print(f"⚠️ 重试中({attempt+1}/{retries}): {str(e)} | 等待{delay}秒")
                time.sleep(delay)
            else:
                print(f"🚨 最终失败: {str(e)}")
                return None

def main():
    all_ips = set()
    print("="*50)
    print(f"🚀 开始抓取 {len(TARGETS)} 个源站 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    for idx, url in enumerate(TARGETS):
        print(f"\n🔍 [{idx+1}/{len(TARGETS)}] 抓取 {url}")
        html = fetch_with_retry(url)
        if html:
            ips = extract_ips(html)
            print(f"✅ 发现 {len(ips)} 个有效IP")
            all_ips.update(ips)
        time.sleep(random.uniform(1, 2))  # 请求间隔
    
    # 获取仓库绝对路径
    repo_path = os.getcwd()
    output_file = os.path.join(repo_path, "cf_ips.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(ip + "\n" for ip in sorted(all_ips))
    
    print("\n" + "="*50)
    print(f"🎉 完成！共获取 {len(all_ips)} 个唯一IP")
    print(f"📁 文件路径: {output_file}")
    print("="*50)

if __name__ == "__main__":
    main()
