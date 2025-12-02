import requests
import re
import csv
import json

# ================= 配置 =================
# 目标 API (vps789 后台接口)
url = "https://vps789.com/public/sum/cfIpApi"
# 提取数量
limit = 10
# =======================================

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://vps789.com',
    'Referer': 'https://vps789.com/cfip?remarks=ip'
}

final_ips = []
seen_ips = set()

print(f"正在抓取 vps789 优选 IP (前 {limit} 个)...")

try:
    # 发送 POST 请求 (注意：必须是 POST)
    response = requests.post(url, json={}, headers=headers, timeout=15)

    if response.status_code == 200:
        # 获取响应文本
        resp_text = response.text
        
        # 使用正则直接提取 IP (防止 JSON 解析报错)
        # 这个正则会按网页上的顺序提取 IP
        ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        found_ips = re.findall(ip_pattern, resp_text)
        
        print(f"接口返回了 {len(found_ips)} 个潜在 IP")
        
        # 筛选前 10 个
        for ip in found_ips:
            # 达到数量就停止
            if len(final_ips) >= limit:
                break
            
            # 简单的 IP 校验 (排除 0.0.0.0)
            if ip != '0.0.0.0' and ip not in seen_ips:
                seen_ips.add(ip)
                final_ips.append(ip)
        
        print(f"成功提取: {len(final_ips)} 个")
        
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(f"错误详情: {response.text[:100]}")

except Exception as e:
    print(f"脚本执行出错: {e}")

# 写入 CSV
filename = 'ip.csv'
try:
    # newline='' 防止产生空行
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        if not final_ips:
            print("警告: 未抓取到 IP，生成的 csv 为空")
        
        for ip in final_ips:
            writer.writerow([f"{ip}:2083"])
            
    print(f"文件已保存: {filename}")

except Exception as e:
    print(f"写入文件失败: {e}")
