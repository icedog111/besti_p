import requests
import csv
import json
from datetime import datetime

# =================配置区域=================
# vps789 数据接口 (POST)
url = "https://vps789.com/public/sum/cfIpApi"

# 筛选条件：提交时间必须早于多少天前
# > 2 天，意味着保留 3天、4天、5天...前提交的 IP
days_threshold = 2
# ==========================================

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://vps789.com',
    'Referer': 'https://vps789.com/cfip?remarks=ip'
}

final_ips = []
seen_ips = set()

print(f"正在获取数据: {url}")
print(f"筛选标准: 保留提交时间 > {days_threshold} 天的 IP")

try:
    # 必须使用 POST 请求
    response = requests.post(url, json={}, headers=headers, timeout=15)
    
    if response.status_code == 200:
        try:
            # 解析 JSON 列表
            data_list = response.json()
            print(f"接口返回总数据量: {len(data_list)} 条")
            
            # 获取当前时间
            now = datetime.now()
            
            for item in data_list:
                # 提取字段 (防止某些数据缺失字段导致报错)
                ip = item.get('ip')
                time_str = item.get('time') # 格式如: "2023-11-20 14:00:00"
                
                if not ip or not time_str:
                    continue
                
                try:
                    # 1. 将字符串时间转为 Python 时间对象
                    ip_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    
                    # 2. 计算差距 (当前时间 - 提交时间)
                    delta = now - ip_time
                    
                    # 3. 判断天数
                    # 如果差距天数 > 2 (即 3, 4, 5...)
                    if delta.days > days_threshold:
                        # 去重并添加
                        if ip not in seen_ips and ip != '0.0.0.0':
                            seen_ips.add(ip)
                            final_ips.append(ip)
                            # 调试日志：显示保留的 IP 和它的天数
                            # print(f"  保留: {ip} (提交于 {delta.days} 天前)")
                            
                except ValueError:
                    # 如果时间格式不对，跳过
                    continue

            print(f"筛选完成！符合条件 (>2天) 的 IP 数量: {len(final_ips)}")
            
        except json.JSONDecodeError:
            print("解析 JSON 失败，API 返回内容可能不正确。")
            print(f"返回内容片段: {response.text[:100]}")
    else:
        print(f"请求失败，状态码: {response.status_code}")

except Exception as e:
    print(f"发生错误: {e}")

# 写入 CSV 文件
filename = 'ip.csv'
try:
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        if not final_ips:
            print("警告：没有找到符合条件的 IP，ip.csv 为空。")
        
        for ip in final_ips:
            writer.writerow([f"{ip}:2083"])
            
    if final_ips:
        print(f"文件已保存: {filename}")

except Exception as e:
    print(f"写入文件失败: {e}")
