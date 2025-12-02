import requests
import re
import csv
import json
from datetime import datetime
from bs4 import BeautifulSoup

# ================= 通用配置 =================
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
final_ips = []
seen_ips = set()

def is_valid_ip(ip):
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

# ================= 模块 1: vps789 (时间筛选 > 2天) =================
def fetch_vps789():
    url = "https://vps789.com/public/sum/cfIpApi"
    print(f"\n[1/3] 正在处理 vps789 (筛选提交时间 > 2天)...")
    
    # 模拟真实请求头
    vps_headers = headers.copy()
    vps_headers.update({
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://vps789.com',
        'Referer': 'https://vps789.com/cfip?remarks=ip'
    })

    try:
        # 必须 POST 请求
        response = requests.post(url, json={}, headers=vps_headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # 兼容处理：有时候数据在 data 字段，有时候是列表
            target_list = []
            if isinstance(data, list):
                target_list = data
            elif isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                target_list = data['data']
            elif isinstance(data, dict) and 'rows' in data and isinstance(data['rows'], list):
                target_list = data['rows']

            now = datetime.now()
            count = 0
            
            for item in target_list:
                if not isinstance(item, dict): continue
                
                ip = item.get('ip')
                time_str = item.get('time')
                
                if ip and time_str:
                    try:
                        # 解析时间
                        ip_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                        delta = now - ip_time
                        
                        # 核心筛选: 大于 2 天
                        if delta.days > 2:
                            if ip not in seen_ips and is_valid_ip(ip):
                                seen_ips.add(ip)
                                final_ips.append(ip)
                                count += 1
                    except ValueError:
                        continue
            print(f"  -> 成功提取 {count} 个符合时间条件的 IP")
        else:
            print(f"  -> 请求失败: {response.status_code}")
    except Exception as e:
        print(f"  -> 出错: {e}")

# ================= 模块 2: Uouin (速度排序取前 6) =================
def parse_speed(speed_str):
    """辅助函数: 统一速度单位为 MB/s"""
    s = speed_str.upper().strip()
    match = re.search(r'(\d+\.?\d*)', s)
    if not match: return 0.0
    val = float(match.group(1))
    if 'KB' in s: val /= 1024
    return val

def fetch_uouin():
    url = "https://api.uouin.com/cloudflare.html"
    print(f"\n[2/3] 正在处理 Uouin (按速度排序取前 6)...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')
            candidates = []
            
            for row in rows:
                text = row.get_text()
                # 提取 IP
                ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)
                if ip_match:
                    ip = ip_match.group()
                    # 提取速度
                    speed = 0.0
                    # 优先查找单元格
                    for col in row.find_all(['td', 'th']):
                        c_text = col.get_text().upper()
                        if 'MB/S' in c_text or 'KB/S' in c_text:
                            speed = parse_speed(c_text)
                            break
                    # 兜底查找整行
                    if speed == 0.0:
                        sm = re.search(r'(\d+\.?\d*)\s*(MB/s|kB/s)', text, re.IGNORECASE)
                        if sm: speed = parse_speed(sm.group(0))
                    
                    if speed > 0 and is_valid_ip(ip):
                        candidates.append({'ip': ip, 'speed': speed})
            
            # 按速度降序排序
            candidates.sort(key=lambda x: x['speed'], reverse=True)
            
            # 取前 6 个
            count = 0
            for item in candidates[:6]:
                ip = item['ip']
                if ip not in seen_ips:
                    seen_ips.add(ip)
                    final_ips.append(ip)
                    count += 1
            print(f"  -> 成功提取 {count} 个高速 IP")
            
        else:
            print(f"  -> 请求失败: {response.status_code}")
    except Exception as e:
        print(f"  -> 出错: {e}")

# ================= 模块 3: cf.090227 (提取所有) =================
def fetch_090227():
    url = "https://cf.090227.xyz/ct?ips=6"
    print(f"\n[3/3] 正在处理 cf.090227 (提取所有)...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            # 简单粗暴正则提取所有 IP
            found_ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response.text)
            count = 0
            for ip in found_ips:
                if ip not in seen_ips and is_valid_ip(ip):
                    seen_ips.add(ip)
                    final_ips.append(ip)
                    count += 1
            print(f"  -> 成功提取 {count} 个 IP")
        else:
            print(f"  -> 请求失败: {response.status_code}")
    except Exception as e:
        print(f"  -> 出错: {e}")

# ================= 主执行流程 =================
if __name__ == "__main__":
    # 依次执行任务
    fetch_vps789()
    fetch_uouin()
    fetch_090227()

    # 写入文件
    filename = 'ip.csv'
    print(f"\n正在写入 {filename} ...")
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not final_ips:
                print("警告: 最终列表为空！")
            
            for ip in final_ips:
                writer.writerow([f"{ip}:2083"])
                
        print(f"任务完成！总共保存 {len(final_ips)} 个唯一 IP。")
        
    except Exception as e:
        print(f"写入文件失败: {e}")
