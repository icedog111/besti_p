import requests
import csv
import json
import re

# ==========================================
# 核心配置：vps789 的真实数据接口
# ==========================================
# 注意：这是一个 API 接口，必须用 POST 请求
api_url = "https://vps789.com/public/sum/cfIpApi"
limit = 10
# ==========================================

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://vps789.com',
    'Referer': 'https://vps789.com/cfip?remarks=ip'
}

final_ips = []
seen_ips = set()

print(f"正在请求 API 接口: {api_url}")

try:
    # 关键修改：使用 POST 请求，并传递空数据 payload
    # 很多 API 如果用 GET 会报 404 或 405
    response = requests.post(api_url, json={}, headers=headers, timeout=15)
    
    if response.status_code == 200:
        print("接口请求成功！正在解析数据...")
        
        try:
            # 1. 解析 JSON 数据
            data = response.json()
            
            # 2. 提取 IP
            # vps789 的 API 返回通常是一个列表，每一项里有 'ip' 字段
            # 我们先尝试把它转成字符串，用正则暴力提取，这样最稳，不怕结构变动
            text_data = json.dumps(data)
            ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
            
            # 正则提取所有 IP
            # API 返回的顺序通常就是网页显示的顺序（按速度排序）
            found_ips = re.findall(ip_pattern, text_data)
            
            print(f"API 返回了 {len(found_ips)} 个 IP")
            
            # 3. 截取前 10 个
            for ip in found_ips:
                if len(final_ips) >= limit:
                    break
                
                # 简单的合法性检查
                if ip != '0.0.0.0' and ip not in seen_ips:
                    seen_ips.add(ip)
                    final_ips.append(ip)
            
            print(f"成功筛选出前 {len(final_ips)} 个优选 IP")
            
        except json.JSONDecodeError:
            print("错误：返回内容不是有效的 JSON 格式。")
            print(f"返回内容片段: {response.text[:100]}")
            
    else:
        print(f"请求失败，状态码: {response.status_code}")
        # 如果 vps789 彻底无法访问，尝试去备用源抓一个 Top 10，保证不交白卷
        print("尝试使用备用源 (Top 10 IP)...")
        try:
            backup_url = "https://ip.164746.xyz/ipTop10.html"
            backup_resp = requests.get(backup_url, timeout=10)
            found_backup = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', backup_resp.text)
            for ip in found_backup[:limit]:
                if ip not in seen_ips:
                    seen_ips.add(ip)
                    final_ips.append(ip)
        except:
            pass

except Exception as e:
    print(f"发生异常: {e}")

# 写入 CSV
filename = 'ip.csv'
try:
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not final_ips:
            print("警告：没有提取到任何 IP。")
        else:
            for ip
