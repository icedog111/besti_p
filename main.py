import requests
import re
import csv
import time
from datetime import datetime
from bs4 import BeautifulSoup

# Selenium 模块
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ================= 全局配置 =================
final_ips = []
seen_ips = set()

# 通用请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def is_valid_ip(ip):
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

# ================= 模块 1: vps789 (Selenium 网页提取) =================
def setup_driver():
    """配置无头 Chrome 浏览器"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    return webdriver.Chrome(options=chrome_options)

def fetch_vps789():
    url = "https://vps789.com/cfip/?remarks=ip"
    print(f"\n[1/3] 正在处理 vps789 (Selenium 网页提取 > 2天)...")
    
    driver = None
    try:
        driver = setup_driver()
        driver.get(url)
        
        # 等待表格加载
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "tbody"))
            )
            time.sleep(3) # 额外等待渲染
        except:
            print("  -> 等待超时，尝试直接解析...")

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        rows = soup.find_all('tr')
        
        count = 0
        now = datetime.now()
        
        for row in rows:
            text = row.get_text(separator=" ", strip=True)
            
            # 提取 IP
            ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)
            if not ip_match: continue
            ip = ip_match.group()
            
            # 提取时间 (支持 "5天" 或 "2023-11-01")
            days_ago = 0
            day_match = re.search(r'(\d+)\s*天', text)
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
            
            if day_match:
                days_ago = int(day_match.group(1))
            elif date_match:
                try:
                    dt = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                    days_ago = (now - dt).days
                except: pass
            
            # 筛选条件: > 2 天
            if days_ago > 2:
                if ip not in seen_ips and is_valid_ip(ip):
                    seen_ips.add(ip)
                    final_ips.append(ip)
                    count += 1
        
        print(f"  -> 成功提取 {count} 个符合条件的 IP")

    except Exception as e:
        print(f"  -> vps789 出错: {e}")
    finally:
        if driver:
            driver.quit()

# ================= 模块 2: Uouin (速度前6) =================
def parse_speed(speed_str):
    s = speed_str.upper().strip()
    match = re.search(r'(\d+\.?\d*)', s)
    if not match: return 0.0
    val = float(match.group(1))
    if 'KB' in s: val /= 1024
    return val

def fetch_uouin():
    url = "https://api.uouin.com/cloudflare.html"
    print(f"\n[2/3] 正在处理 Uouin (速度前 6)...")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')
            candidates = []
            
            for row in rows:
                text = row.get_text()
                ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)
                if ip_match:
                    ip = ip_match.group()
                    speed = 0.0
                    for col in row.find_all(['td', 'th']):
                        c_text = col.get_text().upper()
                        if 'MB/S' in c_text or 'KB/S' in c_text:
                            speed = parse_speed(c_text)
                            break
                    if speed == 0.0:
                        sm = re.search(r'(\d+\.?\d*)\s*(MB/s|kB/s)', text, re.IGNORECASE)
                        if sm: speed = parse_speed(sm.group(0))
                    
                    if speed > 0 and is_valid_ip(ip):
                        candidates.append({'ip': ip, 'speed': speed})
            
            candidates.sort(key=lambda x: x['speed'], reverse=True)
            
            count = 0
            for item in candidates[:6]:
                if item['ip'] not in seen_ips:
                    seen_ips.add(item['ip'])
                    final_ips.append(item['ip'])
                    count += 1
            print(f"  -> 成功提取 {count} 个")
    except Exception as e:
        print(f"  -> Uouin 出错: {e}")

# ================= 模块 3: cf.090227 (提取所有) =================
def fetch_090227():
    url = "https://cf.090227.xyz/ct?ips=6"
    print(f"\n[3/3] 正在处理 cf.090227 (提取所有)...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            found = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response.text)
            count = 0
            for ip in found:
                if ip not in seen_ips and is_valid_ip(ip):
                    seen_ips.add(ip)
                    final_ips.append(ip)
                    count += 1
            print(f"  -> 成功提取 {count} 个")
    except Exception as e:
        print(f"  -> cf.090227 出错: {e}")

# ================= 主程序 =================
if __name__ == "__main__":
    # 执行顺序
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
                print("警告: 结果列表为空")
            for ip in final_ips:
                writer.writerow([f"{ip}:2083"])
        print(f"任务完成！共保存 {len(final_ips)} 个唯一 IP。")
    except Exception as e:
        print(f"写入失败: {e}")
