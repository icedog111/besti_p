import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表
urls = [
    'https://ip.164746.xyz/ipTop10.html',
    'https://cf.090227.xyz',
    'https://api.uouin.com/cloudflare.html',
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://stock.hostmonit.com/CloudFlareYes'
]

# 模拟浏览器 User-Agent，防止被 403 拦截
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# 简单的 IP 匹配正则
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 用于存储去重后的 IP
unique_ips = set()

def is_valid_ip(ip):
    """验证 IP 是否合法 (0-255)"""
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        i = int(part)
        if i < 0 or i > 255:
            return False
    return True

print("开始抓取...")

for url in urls:
    try:
        print(f"正在处理: {url}")
        # 发送HTTP请求，添加 headers 和 timeout
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"  - 跳过: 状态码 {response.status_code}")
            continue

        response.encoding = 'utf-8'
        
        # 策略优化：与其针对每个网站写特定解析器，不如直接在整个网页文本中正则提取
        # 这样即使网站改版（比如 li 变成了 tr），只要 IP 还在页面上就能抓到
        # 对于简单的 IP 抓取，这是最鲁棒的方法
        
        text_content = response.text
        # 如果需要更精准，可以保留你的 BeautifulSoup 逻辑，但在 Action 中建议用暴力正则兼容性更好
        
        ip_matches = re.findall(ip_pattern, text_content)

        count = 0
        for ip in ip_matches:
            if is_valid_ip(ip):
                if ip not in unique_ips:
                    unique_ips.add(ip)
                    count += 1
        
        print(f"  - 成功提取 {count} 个新 IP")

    except Exception as e:
        print(f"  - 出错: {e}")

# 写入文件
if unique_ips:
    with open('ip.txt', 'w', encoding='utf-8') as file:
        for ip in sorted(unique_ips):
            file.write(ip + '\n')
    print(f"\n总计写入 {len(unique_ips)} 个唯一 IP 到 ip.txt")
else:
    print("\n未找到任何有效 IP。")
