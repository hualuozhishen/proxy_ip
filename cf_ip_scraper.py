import requests
import re
import socket
import time
import random
import logging
from datetime import datetime
from bs4 import BeautifulSoup

# 配置日志 (关键调试)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# 多源配置 (含备用源)
SOURCE_CONFIG = [
    {"url": "https://www.wetest.vip/page/cloudflare/address_v4.html", "type": "html"},
    {"url": "https://ip.164746.xyz", "type": "text"},
    {"url": "https://cf.090227.xyz", "type": "text"},
    {"url": "https://stock.hostmonit.com/CloudFlareYes", "type": "text"},
    {"url": "https://monitor.gacjie.cn/page/cloudflare/ipv4.html", "type": "html"}  # 备用源
]

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
]

def fetch_with_retry(url, max_retries=3):
    """带指数退避的重试机制"""
    for attempt in range(max_retries):
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            response = requests.get(
                url, 
                headers=headers, 
                timeout=(3, 5),  # 连接3s/读取5s超时
                verify=False
            )
            response.raise_for_status()
            return response.text
        except (requests.ConnectionError, requests.Timeout) as e:
            wait = 2 ** attempt + random.uniform(0, 1)
            logger.warning(f"Attempt {attempt+1} failed: {e}. Retrying in {wait:.1f}s")
            time.sleep(wait)
    return None

def parse_html_source(html):
    """解析HTML表格型数据源"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        return [td.text.strip() for td in soup.select('table td:first-child') 
                if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', td.text.strip())]
    except Exception as e:
        logger.error(f"HTML解析失败: {str(e)}")
        return []

def parse_text_source(text):
    """解析纯文本IP列表"""
    try:
        return list(set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text)))
    except Exception as e:
        logger.error(f"文本解析失败: {str(e)}")
        return []

def test_latency(ip, port=443, timeout=1.5):
    """TCP协议层延迟测试 (避开HTTPS证书问题)"""
    start = time.time()
    try:
        sock = socket.create_connection((ip, port), timeout=timeout)
        sock.close()
        return int((time.time() - start) * 1000)
    except socket.timeout:
        return 9999
    except Exception:
        return 9998  # 连接拒绝等错误

def main():
    all_ips = []
    logger.info(f"▶ 开始抓取任务 {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}")
    
    # 多源并行抓取 + 独立容错
    for source in SOURCE_CONFIG:
        try:
            logger.info(f"▷ 抓取源: {source['url']}")
            content = fetch_with_retry(source['url'])
            if not content:
                continue
                
            ips = parse_html_source(content) if source['type'] == "html" else parse_text_source(content)
            valid_ips = [ip for ip in ips if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip)]
            all_ips.extend(valid_ips)
            logger.info(f"  ✓ 有效IP: {len(valid_ips)}")
        except Exception as e:
            logger.error(f"❗ 源 {source['url']} 处理异常: {str(e)}", exc_info=True)
    
    # 全局去重
    unique_ips = list(set(all_ips))
    logger.info(f"★ 总去重IP: {len(unique_ips)}")
    
    # 延迟测试 (仅测前100个避免超时)
    fast_ips = []
    for ip in unique_ips[:100]:  # 限流防止Action超时
        latency = test_latency(ip)
        if latency < 150:
            fast_ips.append((ip, latency))
    fast_ips.sort(key=lambda x: x[1])
    
    # 生成报告
    report = [
        "# Cloudflare优选IP列表 | 更新时间: {}".format(datetime.utcnow().strftime("%Y-%m-%d %H:%M")),
        "# 来源: " + ", ".join([s["url"] for s in SOURCE_CONFIG]),
        "# 总IP数量: {}\n".format(len(unique_ips)),
        "## 五星推荐 IP (延迟 < 150ms)\n```"
    ]
    report += [ip for ip, _ in fast_ips]
    report.append("```")
    
    # 写入文件
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
    logger.info(f"✅ 生成优选IP: {len(fast_ips)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"💥 主流程崩溃: {str(e)}", exc_info=True)
        exit(1)  # 明确错误码
