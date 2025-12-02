import requests
import re
import csv
import json

# =================配置区域=================
# 真实的 API 接口地址 (不再是前端页面)
api_url = "https://vps789.com/public/sum/cfIpApi"
limit = 10
# ==========================================

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Referer': 'https://vps789.com/'
}

final_ips = []
seen_ips = set()

print(f"开始调用 API: {api_url}")

try:
    # 1. 尝试 GET 请求
    response = requests.get(api_url, headers=headers, timeout=15)
    
    # 如果 GET 失败 (405 Method Not Allowed)，尝试 POST
    if response.status_code == 405 or response.status_code == 404:
        print(f"GET 请求返回 {response.status_code}，尝试 POST 请求...")
        response = requests.post(api_url, headers=headers, timeout=15)

    if response.status_code == 200:
        print("API 请求成功，正在解析 JSON...")
        
        try:
            # 尝试解析 JSON
            data = response.json()
            
            # vps789 的 API 返回结构通常是列表，或者包含在 'data' 字段里
            # 我们先尝试把所有可能的 IP 字符串提取出来
            # 无论 JSON 结构多复杂，转成字符串后正则提取是最稳的方法
            text_dump = json.dumps(data)
            ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
            found_ips = re.findall(ip_pattern, text_dump)
            
            print(f"从 API 数据中匹配到 {len(found_ips)} 个潜在 IP")
            
            for ip in found_ips:
                if len(final_ips) >= limit:
                    break
                
                # 简单验证 IP 格式
                if ip not in seen_ips and ip != '0.0.0.0':
                    seen_ips.add(ip)
                    final_ips.append(ip)
                    
        except json.JSONDecodeError:
            print("API 返回的不是 JSON，尝试直接正则提取...")
            found_ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', response.text)
            for ip in found_ips:
                if len(final_ips) >= limit: break
                if ip not in seen_ips:
                    seen_ips.add(ip)
                    final_ips.append(ip)

        print(f"成功提取前 {len(final_ips)} 个 IP")
        
    else:
        print(f"API 请求失败，状态码: {response.status_code}")
        print(f"返回内容片段: {response.text[:100]}")

except Exception as e:
    print(f"发生错误: {e}")

# 写入 CSV 文件
filename = 'ip.csv'
try:
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not final_ips:
            print("警告：没有提取到 IP，ip.csv 为空。")
        else:
            for ip in final_ips:
                writer.writerow([f"{ip}:2083"])
            print(f"文件已保存: {filename}")

except Exception as e:
    print(f"写入文件失败: {e}")
