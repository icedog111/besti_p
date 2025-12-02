import requests
import re
import csv

# =================配置区域=================
# 使用 vps789 的数据源
url = "https://vps789.com/cfip/?remarks=ip"
# 限制提取前 10 个
limit = 10
# ==========================================

headers = {
    # 使用更真实的浏览器头信息
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
}

# 匹配 IPv4 的正则表达式
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
final_ips = []
seen_ips = set()

def is_valid_ip(ip):
    """验证 IP 是否合法 (排除类似 999.999.999.999 的错误匹配)"""
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False

print(f"开始抓取: {url}")

try:
    response = requests.get(url, headers=headers, timeout=20)
    
    if response.status_code == 200:
        print("网页请求成功，正在解析...")
        # 调试：打印一下网页内容的长度，如果太短说明可能被拦截了
        print(f"网页内容长度: {len(response.text)} 字符")
        
        # 使用正则在整个网页文本中查找所有 IP
        # 这种方式比解析 HTML 表格更稳定，即使数据在 JS 里也能抓到
        found_ips = re.findall(ip_pattern, response.text)
        
        print(f"原始匹配到 {len(found_ips)} 个潜在 IP")

        for ip in found_ips:
            # 如果已经凑够了 10 个，就停止
            if len(final_ips) >= limit:
                break
            
            # 验证 IP 且不重复
            if is_valid_ip(ip) and ip not in seen_ips:
                seen_ips.add(ip)
                final_ips.append(ip)
        
        print(f"筛选出前 {len(final_ips)} 个有效 IP")
        
    else:
        print(f"请求失败，状态码: {response.status_code}")

except Exception as e:
    print(f"发生错误: {e}")

# 写入 CSV 文件
filename = 'ip.csv'
try:
    # 无论是否抓取到 IP，都进行写入（即使为空），防止 Action 找不到文件报错
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not final_ips:
            print("警告：未提取到任何 IP，生成的 CSV 为空。")
        
        for ip in final_ips:
            writer.writerow([f"{ip}:2083"])
            
    if final_ips:
        print(f"成功！已保存到 {filename}")

except Exception as e:
    print(f"写入文件失败: {e}")
