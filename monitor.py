import requests
import os

# 换成这个更稳的全球搜索接口
API_URL = "https://careers.microsoft.com/api/search/jobs?lc=Suzhou%2C%20China&et=Internship&exp=Students%20and%20graduates"

def main():
    history_file = "visited_jobs.txt"
    visited = set()
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            visited = set(f.read().splitlines())

    # 更加真实的浏览器伪装
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://careers.microsoft.com/v2/global/en/locations/suzhou.html"
    }
    
    webhook = os.getenv("FEISHU_WEBHOOK")
    
    try:
        # 获取数据
        resp = requests.get(API_URL, headers=headers, timeout=30)
        
        # 如果不是 200，说明被拦截了
        if resp.status_code != 200:
            raise Exception(f"服务器拒绝访问，状态码：{resp.status_code}")
            
        data = resp.json()
        # 微软这个新接口的数据结构在 operationResult.result.jobs 里
        jobs = data.get('operationResult', {}).get('result', {}).get('jobs', [])
        total_count = len(jobs)
        
    except Exception as e:
        error_msg = f"❌ 微软监控运行出错：{str(e)}\n提示：可能是接口被拦截，建议稍后再试。"
        requests.post(webhook, json={"msg_type": "text", "content": {"text": error_msg}})
        return

    new_found = []
    for job in jobs:
        # 这个接口的字段名略有不同
        job_id = str(job.get('jobId', ''))
        if job_id and job_id not in visited:
            title = job.get('title', '未知岗位')
            # 提取能力要求（在 properties.description 中）
            desc = job.get('properties', {}).get('description', "").lower()
            
            # 简单技能汇集
            skills = []
            for s in ["Python", "C++", "C#", "Java", "Algorithm", "Azure", "AI"]:
                if s.lower() in desc: skills.append(s)
            skills_str = " / ".join(skills) if skills else "见详情"
            
            # 这里的链接格式也略有变化
            link = f"https://careers.microsoft.com/us/en/job/{job_id}"
            new_found.append(f"🚀 微软苏州新岗位：{title}\n🔑 技能：{skills_str}\n🔗 链接：{link}")
            visited.add(job_id)

    # 推送逻辑
    if new_found:
        report_text = f"【微软实习监控 - 发现更新】\n\n" + "\n\n".join(new_found)
        requests.post(webhook, json={"msg_type": "text", "content": {"text": report_text}})
        with open(history_file, "w") as f:
            f.write("\n".join(visited))
    else:
        safe_msg = f"✅ 微软监控报平安：目前苏州共有 {total_count} 个实习岗位，暂无新增。"
        requests.post(webhook, json={"msg_type": "text", "content": {"text": safe_msg}})

if __name__ == "__main__":
    main()
