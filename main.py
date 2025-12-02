import requests
import csv
import json
from datetime import datetime, timedelta

# =================配置区域=================
url = "https://vps789.com/public/sum/cfIpApi"
# 筛选条件：保留提交时间超过多少天的 IP
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

print(f"开始请求 API: {url}")
print(f"筛选条件: 提交时间距今 > {days_threshold} 天")

try:
    # 发送 POST 请求
    response = requests.post(url, json={}, headers=headers, timeout=15)
    
    if response.status_code == 200:
        try:
            # 解析 JSON 数据
            data_list = response.json()
            
            # vps789 的数据通常是一个列表，每一项是字典
            # 格式示例: {"ip": "1.1.1.1", "time": "2023-12-01 12:00:00", ...}
            
            print(f"API 返回数据条数: {len(data_list)}")
            
            # 获取当前时间
            now = datetime.now()
            
            count_pass = 0
            
            for item in data_list:
                # 提取 IP 和 时间
                # 注意：这里假设 API 返回的键名为 'ip' 和 'time'
                # 如果键名变了，这里需要相应修改，但通常是这两个
                ip = item.get('ip')
                time_str = item.get('time') 
                
                if not ip or not time_str:
                    continue
                
                try:
                    # 1. 将时间字符串转换为时间对象
                    # 格式通常为 "2023-12-01 12:30:00"
                    ip_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    
                    # 2. 计算时间差 (当前时间 - 提交时间)
                    delta = now - ip_time
                    
                    # 3. 判断是否大于 2 天
                    if delta.days > days_threshold:
                        # 4. 去重并添加
                        if ip not in seen_ips and ip != '0.0.0.0':
                            seen_ips.add(ip)
                            final_ips.append(ip)
                            count_pass += 1
                            # print(f"  保留: {ip} (已提交 {delta.days} 天)")
                            
                except ValueError:
                    # 如果时间格式解析失败，跳过该条
                    continue

            print(f"筛选完成！符合条件(>{days_threshold}天)的 IP 数量: {len(final_ips)}")
            
        except json.JSONDecodeError:
            print("错误：无法解析 API 返回的 JSON 数据")
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
            print("警告：没有符合筛选条件的 IP，ip.csv 为空。")
        
        for ip in final_ips:
            writer.writerow([f"{ip}:2083"])
            
    if final_ips:
        print(f"文件已保存: {filename}")

except Exception as e:
    print(f"写入文件失败: {e}")
