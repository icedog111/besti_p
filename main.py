import requests
import re
import csv
from bs4 import BeautifulSoup

# =================配置区域=================
url = "https://vps789.com/cfip/?remarks=ip"
limit = 10
# ==========================================

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
final_ips = []
seen_ips = set()

def is_valid_ip(ip):
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

print(f"开始抓取表格前 {limit} 名: {url}")

try:
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        response.encoding = 'utf-8'
        
        # 使用 BeautifulSoup 解析 HTML 表格
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 寻找所有的表格行 (tr)
        rows = soup.find_all('tr')
        
        print(f"找到 {len(rows)} 行表格数据，正在筛选...")
        
        for row in rows:
            # 已经提取够了就停止
            if len(final_ips) >= limit:
                break
                
            # 获取这一行的文本内容
            row_text = row.get_text()
            
            # 在这一行里查找 IP
            ip_match = re.search(ip_pattern, row_text)
            
            if ip_match:
                ip = ip_match.group()
                
                # 验证有效性并去重
                if is_valid_ip(ip) and ip not in seen_ips:
                    seen_ips.add(ip)
                    final_ips.append(ip)
                    # 打印日志，显示进度
                    print(f"  [{len(final_ips)}] 提取到: {ip}")
        
        print(f"\n提取完成，共获取 {len(final_ips)} 个 IP")
        
    else:
        print(f"请求失败，状态码: {response.status_code}")

except Exception as e:
    print(f"发生错误: {e}")

# 写入 CSV 文件 (无标题，带端口)
filename = 'ip.csv'
try:
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for ip in final_ips:
            writer.writerow([f"{ip}:2083"])
            
    print(f"文件已保存: {filename}")

except Exception as e:
    print(f"写入文件失败: {e}")
