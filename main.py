import requests
import re
import csv
from bs4 import BeautifulSoup

# ================= 配置区域 =================
url = "https://api.uouin.com/cloudflare.html"
limit = 6  # 提取最快的 6 个
# ==========================================

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

final_ips = []
candidates = [] # 用于存储 (IP, 速度) 的临时列表

# 辅助函数：将速度字符串转换为数字 (统一单位为 MB/s)
def parse_speed(speed_str):
    """
    输入: "25.5 MB/s" 或 "500 kB/s"
    输出: 25.5 (float)
    """
    s = speed_str.upper().strip()
    # 提取数字部分
    match = re.search(r'(\d+\.?\d*)', s)
    if not match:
        return 0.0
    
    value = float(match.group(1))
    
    # 单位换算
    if 'KB' in s:
        value = value / 1024  # 1 MB = 1024 KB
    
    return value

print(f"正在分析网站: {url}")

try:
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 找到所有表格行
        rows = soup.find_all('tr')
        print(f"找到 {len(rows)} 行数据，正在分析速度...")
        
        for row in rows:
            # 获取这一行的所有单元格
            cols = row.find_all(['td', 'th'])
            row_text = row.get_text()
            
            # 1. 提取 IP (使用正则)
            ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', row_text)
            if not ip_match:
                continue
            ip = ip_match.group()
            
            # 2. 提取速度
            # 遍历这一行的每个格子，找包含 "MB/S" 或 "KB/S" 的内容
            speed_value = 0.0
            for col in cols:
                cell_text = col.get_text().strip()
                if 'MB/s' in cell_text or 'kB/s' in cell_text or 'MB/S' in cell_text:
                    speed_value = parse_speed(cell_text)
                    break # 找到速度列后停止查找该行
            
            # 如果没在格子里找到，尝试整行匹配 (兜底策略)
            if speed_value == 0.0:
                speed_match = re.search(r'(\d+\.?\d*)\s*(MB/s|kB/s)', row_text, re.IGNORECASE)
                if speed_match:
                    speed_value = parse_speed(speed_match.group(0))
            
            # 只有速度大于0才加入候选
            if speed_value > 0:
                candidates.append({'ip': ip, 'speed': speed_value})
        
        # === 核心步骤：按速度从大到小排序 ===
        # reverse=True 表示降序 (大到小)
        candidates.sort(key=lambda x: x['speed'], reverse=True)
        
        print(f"提取并排序了 {len(candidates)} 个有效 IP")
        
        # 取前 6 个
        for item in candidates[:limit]:
            final_ips.append(item['ip'])
            print(f"  -> 选中: {item['ip']} (速度: {item['speed']:.2f} MB/s)")
            
    else:
        print(f"请求失败，状态码: {response.status_code}")

except Exception as e:
    print(f"发生错误: {e}")

# 写入 CSV
filename = 'ip.csv'
try:
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not final_ips:
            print("警告: 结果为空")
        
        for ip in final_ips:
            writer.writerow([f"{ip}:2083"])
            
    print(f"\n成功保存速度最快的 {len(final_ips)} 个 IP 到 {filename}")

except Exception as e:
    print(f"写入失败: {e}")
