import requests
import os
import random

# 使用这个带区域参数的 API
API_URL = "https://careers.microsoft.com/api/search/jobs?lc=Suzhou%2C%20China&et=Internship"

def main():
    webhook = os.getenv("FEISHU_WEBHOOK")
    history_file = "visited_jobs.txt"
    
    # 随机 User-Agent 列表，让请求看起来更像不同的真人
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]

    headers = {
        "User-Agent": random.choice(ua_list),
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://careers.microsoft.com/v2/global/en/locations/suzhou.html",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"
    }
    
    try:
        # 使用 Session 保持会话，模拟更真实的浏览器行为
        session = requests.Session()
        resp = session.get(API_URL, headers=headers, timeout=30)
        
        # 调试：如果不成功，我们直接看返回的前100个字符是什么
        if resp.status_code != 200:
            raise Exception(f"状态码 {resp.status_code}，内容预览：{resp.text[:100]}")
            
        data = resp.json()
        jobs = data.get('operationResult', {}).get('result', {}).get('jobs', [])
        
        # (后续处理逻辑与之前一致...)
        # ... (此处省略重复的对比发消息代码)
        
    except Exception as e:
        # 如果还是报错，这次我们会把服务器返回的前几个字发到飞书，方便分析
        error_msg = f"❌ 微软监控依然被拦截：\n{str(e)}"
        requests.post(webhook, json={"msg_type": "text", "content": {"text": error_msg}})

if __name__ == "__main__":
    main()
