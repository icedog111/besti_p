import requests
import csv
import json
from datetime import datetime

# =================配置区域=================
url = "https://vps789.com/public/sum/cfIpApi"
# 筛选标准: 提交时间 > 2 天
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

try:
    response = requests.post(url, json={}, headers=headers, timeout=15)
    
    if response.status_code == 200:
        try:
            # 1. 获取原始 JSON
            json_data = response.json()
            
            # 2. 智能提取列表数据
            # 如果返回的是字典 (如 {'code': 200, 'data': [...]})，则提取 'data'
            if isinstance(json_data, dict):
                # 尝试寻找包含数据的键名
                if 'data' in json_data:
                    data_list = json_data['data']
                elif 'rows' in json_data:
                    data_list = json_data['rows']
                else:
                    # 如果找不到常见键名，打印键名帮助调试
                    print(f"警告: 未找到 data 字段，JSON 键名有: {list(json_data.keys())}")
                    data_list = []
            elif isinstance(json_data, list):
                # 如果直接就是列表，直接用
                data_list = json_data
            else:
                data_list = []

            print(f"成功提取数据列表: {len(data_list)} 条")
            
            # 获取当前时间
            now = datetime.now()
            
            for item in data_list:
                # 确保 item 是字典
                if not isinstance(item, dict):
                    continue

                ip = item.get('ip')
                time_str = item.get('time') 
                
                if not ip or not time_str:
                    continue
                
                try:
                    # 解析时间
                    ip_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    
                    # 计算天数差
                    delta = now - ip_time
                    
                    # 筛选 > 2 天
                    if delta.days > days_threshold:
                        if ip not in seen_ips and ip != '0.0.0.0':
                            seen_ips.add(ip)
                            final_ips.append(ip)
                            
                except ValueError:
                    continue

            print(f"筛选完成！符合条件(>{days_threshold}天)的 IP 数量: {len(final_ips)}")
            
        except json.JSONDecodeError:
            print("错误: 无法解析 JSON")
    else:
        print(f"请求失败: {response.status_code}")

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
            
    if final_ips:
        print(f"文件已保存: {filename}")
except Exception as e:
    print(f"写入失败: {e}")
