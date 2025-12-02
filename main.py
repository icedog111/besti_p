import requests
import re
import csv
import os

# 目标 URL 列表
urls = [
    'https://ip.164746.xyz/ipTop10.html',
    'https://cf.090227.xyz',
    'https://api.uouin.com/cloudflare.html',
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://stock.hostmonit.com/CloudFlareYes'
]

# 模拟浏览器 User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# IP 匹配正则
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 使用 set 自动去重
unique_ips = set()

def is_valid_ip(ip):
    """验证 IP 格式"""
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

print("开始执行抓取任务...")

for url in urls:
    try:
        print(f"正在请求: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            response.encoding = 'utf-8'
            found_ips = re.findall(ip_pattern, response.text)
            
            count = 0
            for ip in found_ips:
                if is_valid_ip(ip) and ip not in unique_ips:
                    unique_ips.add(ip)
                    count += 1
            print(f"  -> 成功提取 {count} 个新 IP")
        else:
            print(f"  -> 跳过 (状态码: {response.status_code})")

    except Exception as e:
        print(f"  -> 出错: {e}")

# 写入 CSV 文件
filename = 'ip.csv'
try:
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['IP']) # 表头
        
        for ip in sorted(unique_ips):
            # ▼▼▼ 修改在这里：给 IP 加上 :2083 ▼▼▼
            ip_with_port = f"{ip}:2083"
            writer.writerow([ip_with_port])
            
    print(f"\n成功！共保存 {len(unique_ips)} 个 IP 到 {filename}")

except Exception as e:
    print(f"\n写入文件失败: {e}")
