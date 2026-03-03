import requests
import os
import json

# 微软苏州实习 API
API_URL = "https://apply.careers.microsoft.com/api/careers/search?location=China%2C+Jiangsu%2C+Suzhou&seniority=Intern"

def main():
    # 1. 读取历史记录（防止重复推送）
    history_file = "visited_jobs.txt"
    visited = set()
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            visited = set(f.read().splitlines())

    # 2. 模拟访问
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(API_URL, headers=headers, timeout=15)
        jobs = resp.json().get('jobs', [])
    except Exception as e:
        print(f"网络请求出错: {e}")
        return

    new_found = []
    # 这里的关键词你可以根据你关心的方向自己增加
    skill_keywords = ["Python", "C++", "C#", "Java", "Algorithm", "Azure", "Machine Learning", "React"]

    for job in jobs:
        job_id = str(job.get('jobId'))
        if job_id not in visited:
            title = job.get('title')
            # 简单的能力汇集逻辑：从描述中搜寻关键词
            description = job.get('description', "")
            found_skills = [s for s in skill_keywords if s.lower() in description.lower()]
            skills_str = " / ".join(found_skills) if found_skills else "见详情链接"
            
            link = f"https://apply.careers.microsoft.com/careers/job/{job_id}"
            new_found.append(f"【新岗位】{title}\n🔑 核心技能：{skills_str}\n🔗 链接：{link}")
            visited.add(job_id)

    # 3. 推送至飞书
    if new_found:
        webhook = os.getenv("FEISHU_WEBHOOK")
        report_text = "🚀 发现微软苏州实习更新！\n\n" + "\n\n".join(new_found)
        requests.post(webhook, json={"msg_type": "text", "content": {"text": report_text}})
        
        # 保存新 ID
        with open(history_file, "w") as f:
            f.write("\n".join(visited))
