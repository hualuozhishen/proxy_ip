import requests
import re
import os
import json
from datetime import datetime

# 数据源配置（含商业API与公开源）
SOURCES = [
    "https://iproyal.com/api/residential-proxies/geolocation",  # 住宅IP API [1](@ref)
    "https://raw.githubusercontent.com/ip-scanner/cloudflare/daily-ip-list.txt",  # 公开IP库 [7](@ref)
    "https://ipinfo.io/residential"  # 住宅IP验证服务 [9](@ref)
]

# Scamalytics API配置（需在GitHub Secrets设置）
SCAMALYTICS_API = "https://api.scamalytics.com/ip/"
API_KEY = os.getenv("SCAMALYTICS_KEY")

def fetch_ips(url):
    """从数据源提取住宅IP"""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        # 匹配住宅IP特征（排除数据中心IP）
        ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', resp.text)
        return set(ip for ip in ips if "data-center" not in resp.text)  # 过滤数据中心IP
    except Exception as e:
        print(f"🚨 抓取失败: {url} | 错误: {str(e)}")
        return set()

def rate_ip_cleanliness(ip):
    """IP洁净度星级评估 (基于欺诈分) [9](@ref)"""
    try:
        response = requests.get(f"{SCAMALYTICS_API}{ip}", headers={"Authorization": f"Bearer {API_KEY}"}, timeout=10)
        data = response.json()
        fraud_score = data.get("score", 100)
        
        # 欺诈分转星级 (0-100分 → 1-5星)
        if fraud_score <= 10: return "★★★★★"  # 极优
        elif fraud_score <= 25: return "★★★★☆"  # 优良
        elif fraud_score <= 50: return "★★★☆☆"  # 中等
        elif fraud_score <= 75: return "★★☆☆☆"  # 风险
        else: return "★☆☆☆☆"  # 高危
    except:
        return "★★☆☆☆"  # 默认中等风险

def generate_report(ip_list):
    """生成带星级的Markdown报告"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = f"# 海外住宅IP洁净度报告 | 更新时间: {timestamp}\n\n"
    report += "| IP地址 | 安全星级 | 欺诈分来源 |\n"
    report += "|--------|----------|------------|\n"
    
    for ip in sorted(ip_list):
        rating = rate_ip_cleanliness(ip)
        report += f"| `{ip}` | {rating} | [Scamalytics](https://scamalytics.com/ip/{ip}) |\n"
    
    # 添加统计摘要
    clean_count = sum(1 for ip in ip_list if "★" in rating and rating.count("★") >= 4)
    report += f"\n**统计**：共 {len(ip_list)} 个IP，其中 {clean_count} 个（{clean_count/len(ip_list)*100:.1f}%）达到★★★★☆以上评级"
    return report

if __name__ == "__main__":
    all_ips = set()
    for url in SOURCES:
        print(f"🔍 抓取源: {url}")
        ips = fetch_ips(url)
        print(f"✅ 发现住宅IP: {len(ips)}个")
        all_ips.update(ips)
    
    # 写入报告文件
    with open("REPORT.md", "w", encoding="utf-8") as f:
        f.write(generate_report(all_ips))
    print("🚀 已生成REPORT.md")
