import requests
import re
from bs4 import BeautifulSoup
import datetime
import time
import os

# 配置参数
SOURCES = [
    "https://www.wetest.vip/page/cloudflare/address_v4.html",
    "https://ip.164746.xyz",
    "https://cf.090227.xyz",
    "https://stock.hostmonit.com/CloudFlareYes"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def get_wetest_ips(url):
    """ 解析wetest.vip的表格数据 """
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        return [td.text.strip() for td in soup.select('table td:nth-child(1)')]
    except Exception as e:
        print(f"Error on {url}: {str(e)}")
        return []

def get_text_ips(url):
    """ 解析纯文本IP列表 """
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        return re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', res.text)
    except Exception as e:
        print(f"Error on {url}: {str(e)}")
        return []

def test_latency(ip, port=443):
    """ 测试IP延迟 (单位：毫秒) """
    start = time.time()
    try:
        requests.get(f'https://{ip}', headers=HEADERS, timeout=3, verify=False)
        return int((time.time() - start) * 1000)
    except:
        return 9999  # 超时标记

def generate_report(ip_list):
    """ 生成README内容 """
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    report = [
        "# Cloudflare优选IP列表 | 更新时间: {}\n".format(timestamp),
        "# 来源: {}\n".format(", ".join(SOURCES)),
        "# 总IP数量: {}\n".format(len(ip_list)),
        "\n## 五星推荐 IP (延迟 < 150ms)\n"
    ]
    
    # 添加延迟测试和分级
    fast_ips = []
    for ip in ip_list:
        latency = test_latency(ip)
        if latency < 150:  # 五星标准
            fast_ips.append((ip, latency))
    
    # 按延迟排序
    fast_ips.sort(key=lambda x: x[1])
    
    # 只保留IP地址
    for ip, _ in fast_ips:
        report.append(ip)
    
    return "\n".join(report)

if __name__ == "__main__":
    all_ips = []
    for url in SOURCES:
        if "wetest" in url:
            all_ips += get_wetest_ips(url)
        else:
            all_ips += get_text_ips(url)
    
    # 去重
    unique_ips = list(set(all_ips))
    
    # 生成报告
    report_content = generate_report(unique_ips)
    
    # 保存到文件
    with open('README.md', 'w') as f:
        f.write(report_content)
