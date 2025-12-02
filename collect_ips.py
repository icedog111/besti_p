import requests
import re
import csv
import os

# 目标URL列表
urls = [
    'https://ip.164746.xyz/ipTop10.html',
    'https://cf.090227.xyz',
    'https://api.uouin.com/cloudflare.html',
    'https://www.wetest.vip/page/cloudflare/address_v4.html',
    'https://stock.hostmonit.com/CloudFlareYes'
]

# 模拟浏览器 Header，防止被 403 拦截 (GitHub Actions 必须)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# IP 匹配正则
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 使用 set 进行自动去重
unique_ips = set()

def is_valid_ip(ip):
    """简单验证 IP 数值是否合法 (0-255)"""
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

print("开始抓取 Cloudflare IP...")

# 1. 抓取与解析
for url in urls:
    try:
        print(f"正在请求: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            response.encoding = 'utf-8'
            # 直接在全文中正则搜索，比解析 HTML 结构更稳定，适应性更强
            found_ips = re.findall(ip_pattern, response.text)
            
            new_count = 0
            for ip in found_ips:
                if is_valid_ip(ip) and ip not in unique_ips:
                    unique_ips.add(ip)
                    new_count += 1
            print(f"  -> 成功获取 {new_count} 个新 IP")
        else:
            print(f"  -> 失败: 状态码 {response.status_code}")

    except Exception as e:
        print(f"  -> 出错: {e}")

# 2. 写入 CSV 文件
output_file = 'ip.csv'

# 如果没有抓到 IP，也生成一个空文件或表头，防止 Action 报错找不到文件
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # 写入表头 (Header)
    writer.writerow(['IP'])
    
    # 写入数据
    for ip in sorted(unique_ips):
        writer.writerow([ip])

print(f"\n处理完成！共保存 {len(unique_ips)} 个 IP 到 {output_file}")
