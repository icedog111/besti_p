import requests
import re
import csv

# =================配置区域=================
# 修正后的 URL (去掉 /? 变成了 ?)
# 优先尝试这个地址
primary_url = "https://vps789.com/cfip?remarks=ip"
# 如果上面 404，尝试这个备用地址 (可能是主页)
backup_url = "https://vps789.com/cfip"
limit = 10
# ==========================================

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://vps789.com/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
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

def fetch_ips(url):
    print(f"正在尝试抓取: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            found = re.findall(ip_pattern, resp.text)
            print(f"  -> 状态 200 OK，发现 {len(found)} 个潜在 IP")
            return found
        else:
            print(f"  -> 失败，状态码: {resp.status_code}")
            return []
    except Exception as e:
        print(f"  -> 请求出错: {e}")
        return []

# 1. 尝试主 URL
raw_ips = fetch_ips(primary_url)

# 2. 如果主 URL 没拿到数据 (比如 404)，尝试备用 URL
if not raw_ips:
    print("\n主 URL 抓取失败，尝试备用地址...")
    raw_ips = fetch_ips(backup_url)

# 3. 筛选前 10 个
print("\n正在筛选有效 IP...")
for ip in raw_ips:
    if len(final_ips) >= limit:
        break
    if is_valid_ip(ip) and ip not in seen_ips:
        seen_ips.add(ip)
        final_ips.append(ip)

# 4. 写入文件
filename = 'ip.csv'
try:
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not final_ips:
            print("警告：所有尝试均失败，ip.csv 将为空。")
        else:
            for ip in final_ips:
                writer.writerow([f"{ip}:2083"])
            print(f"成功！已保存 {len(final_ips)} 个 IP 到 {filename}")
except Exception as e:
    print(f"写入文件失败: {e}")
