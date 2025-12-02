import requests
import re
import csv
from bs4 import BeautifulSoup

# ==========================================
# 配置与初始化
# ==========================================
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 全局去重集合
seen_ips = set()
# 最终结果列表
final_ips = []

def is_valid_ip(ip):
    """验证 IP 合法性"""
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

def parse_speed_str(text):
    """辅助函数：从字符串中提取速度数值(MB/s)"""
    text = text.upper()
    try:
        match = re.search(r'(\d+(\.\d+)?)', text)
        if match:
            val = float(match.group(1))
            if 'KB' in text:
                val = val / 1024
            return val
    except:
        pass
    return 0.0

# ==========================================
# 模块: 智能解析速度 (Wetest & Uouin)
# ==========================================
def fetch_top_speed_from_site(url, site_name, limit=5):
    print(f"正在智能分析: {site_name} (目标: 速度最快前 {limit} 个)...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200: return []
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        candidates = []
        
        for row in soup.find_all('tr'):
            text = row.get_text()
            ip_match = re.search(ip_pattern, text)
            if ip_match:
                ip = ip_match.group()
                speed = 0.0
                
                # 策略1: 找表格列中的 MB/S
                for col in row.find_all(['td', 'th']):
                    c_text = col.get_text().upper()
                    if 'MB/S' in c_text or 'KB/S' in c_text:
                        speed = parse_speed_str(c_text)
                        break
                
                # 策略2: 整行文本匹配
                if speed == 0.0:
                    speed_match = re.search(r'(\d+\.?\d*)\s*(MB/s|KB/s)', text, re.IGNORECASE)
                    if speed_match:
                        speed = parse_speed_str(speed_match.group(0))

                if speed > 0 and is_valid_ip(ip):
                    candidates.append({'ip': ip, 'speed': speed})
        
        # 按速度倒序排列
        candidates.sort(key=lambda x: x['speed'], reverse=True)
        
        # 打印调试信息
        for i, item in enumerate(candidates[:limit]):
            print(f"  -> {site_name} Top{i+1}: {item['ip']} (速度 {item['speed']:.2f} MB/s)")
            
        return [item['ip'] for item in candidates[:limit]]

    except Exception as e:
        print(f"  -> {site_name} 出错: {e}")
        return []

# ==========================================
# 主执行逻辑
# ==========================================
print("开始执行多源抓取任务...")

# 1. vps789 (提取 10 个)
# ----------------------------------------
try:
    url = 'https://vps789.com/cfip?remarks=ip'
    target_count = 10  # ▼▼▼ 修改此处为 10 ▼▼▼
    
    print(f"正在请求: {url} (目标: {target_count} 个)")
    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code == 200:
        found = re.findall(ip_pattern, resp.text)
        count = 0
        for ip in found:
            if count >= target_count: break
            if is_valid_ip(ip) and ip not in seen_ips:
                seen_ips.add(ip)
                final_ips.append(ip)
                count += 1
        print(f"  -> vps789 完成: {count} 个")
except Exception as e:
    print(f"  -> vps789 失败: {e}")

# 2. Wetest (提取速度前 5)
# ----------------------------------------
wetest_ips = fetch_top_speed_from_site(
    'https://www.wetest.vip/page/cloudflare/address_v4.html', 
    'wetest.vip', 
    limit=5
)
for ip in wetest_ips:
    if ip not in seen_ips:
        seen_ips.add(ip)
        final_ips.append(ip)

# 3. Uouin (提取速度前 5)
# ----------------------------------------
uouin_ips = fetch_top_speed_from_site(
    'https://api.uouin.com/cloudflare.html', 
    'api.uouin.com', 
    limit=5
)
for ip in uouin_ips:
    if ip not in seen_ips:
        seen_ips.add(ip)
        final_ips.append(ip)

# 4. 其他普通源 (各提取 5 个)
# ----------------------------------------
other_urls = [
    'https://cf.090227.xyz/ct?ips=6',
    'https://ip.164746.xyz/ipTop10.html'
]
for url in other_urls:
    try:
        print(f"正在请求补充源: {url}")
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            found = re.findall(ip_pattern, resp.text)
            count = 0
            for ip in found:
                if count >= 5: break
                if is_valid_ip(ip) and ip not in seen_ips:
                    seen_ips.add(ip)
                    final_ips.append(ip)
                    count += 1
            print(f"  -> 提取: {count} 个")
    except:
        pass

# ==========================================
# 写入文件
# ==========================================
filename = 'ip.csv'
try:
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 无标题
        for ip in final_ips:
            writer.writerow([f"{ip}:2083"])
            
    print(f"\n任务全部完成！")
    print(f"总计 IP 数量: {len(final_ips)}")
    print(f"已保存到 {filename}")

except Exception as e:
    print(f"写入文件失败: {e}")
