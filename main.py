import re
import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# =================配置区域=================
url = "https://vps789.com/cfip/?remarks=ip"
# 筛选标准: 大于 2 天 (即 3天、4天...)
days_threshold = 2
# ==========================================

def setup_driver():
    """配置无头 Chrome 浏览器"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，无界面运行
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    # 模拟真实浏览器 User-Agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

final_ips = []
seen_ips = set()

print(f"启动浏览器，准备访问: {url}")
driver = setup_driver()

try:
    # 1. 打开网页
    driver.get(url)
    
    # 2. 等待网页加载 (等待表格行出现)
    print("正在等待页面数据加载...")
    try:
        # 最多等 20 秒，直到 <tbody> 出现
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody"))
        )
        # 再额外强制等 3 秒，确保数据渲染完全
        time.sleep(3)
    except Exception as e:
        print("等待超时，页面可能未正确加载，尝试继续解析...")

    # 3. 获取渲染后的网页源码
    page_source = driver.page_source
    print(f"页面已加载，源码长度: {len(page_source)}")

    # 4. 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # 找到所有的表格行
    rows = soup.find_all('tr')
    print(f"找到 {len(rows)} 行表格数据")

    # 5. 遍历表格提取数据
    for row in rows:
        text = row.get_text(separator=" ", strip=True)
        
        # 提取 IP (正则)
        ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)
        if not ip_match:
            continue
        ip = ip_match.group()

        # 提取时间/天数
        # 情况 A: 网页显示的是 "5天", "3天" (相对时间)
        day_match = re.search(r'(\d+)\s*天', text)
        
        # 情况 B: 网页显示的是 "2023-11-20" (绝对时间)
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', text)
        
        days_ago = 0
        
        if day_match:
            # 直接提取 "5天" 中的 5
            days_ago = int(day_match.group(1))
        elif date_match:
            # 计算日期差
            try:
                date_obj = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                days_ago = (datetime.now() - date_obj).days
            except:
                pass
        
        # === 核心判断 ===
        # 如果从网页上提取到的天数 > 2，或者通过日期算出 > 2
        if days_ago > days_threshold:
            if ip not in seen_ips and ip != '0.0.0.0':
                seen_ips.add(ip)
                final_ips.append(ip)
                # print(f"  提取到: {ip} (提交时间: {days_ago} 天前)")

    print(f"筛选完成！保留提交时间 > {days_threshold} 天的 IP: {len(final_ips)} 个")

except Exception as e:
    print(f"发生错误: {e}")

finally:
    driver.quit()

# 写入 CSV
filename = 'ip.csv'
try:
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not final_ips:
            print("警告: 结果为空")
        for ip in final_ips:
            writer.writerow([f"{ip}:2083"])
            
    if final_ips:
        print(f"文件已保存: {filename}")
except Exception as e:
    print(f"写入失败: {e}")
