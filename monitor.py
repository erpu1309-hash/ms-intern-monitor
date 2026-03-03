import requests
import os
import json

# 微软苏州实习 API
API_URL = "https://apply.careers.microsoft.com/api/careers/search?location=China%2C+Jiangsu%2C+Suzhou&seniority=Intern"

def main():
    # 1. 尝试读取历史
    history_file = "visited_jobs.txt"
    visited = set()
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            visited = set(f.read().splitlines())

    # 2. 模拟真实浏览器访问
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://apply.careers.microsoft.com/careers"
    }
    
    webhook = os.getenv("FEISHU_WEBHOOK")
    print("正在连接微软官网接口...")
    
    try:
        resp = requests.get(API_URL, headers=headers, timeout=20)
        print(f"服务器响应状态码: {resp.status_code}")
        
        data = resp.json()
        jobs = data.get('jobs', [])
        total_count = len(jobs)
        print(f"本次成功抓取到 {total_count} 个实习岗位。")
    except Exception as e:
        error_msg = f"❌ 微软监控运行出错：{e}"
        requests.post(webhook, json={"msg_type": "text", "content": {"text": error_msg}})
        return

    new_found = []
    skill_keywords = ["Python", "C++", "C#", "Java", "Algorithm", "Azure", "React"]

    for job in jobs:
        job_id = str(job.get('jobId') or "")
        if job_id and job_id not in visited:
            title = job.get('title', '未知岗位')
            description = job.get('description', "")
            found_skills = [s for s in skill_keywords if s.lower() in description.lower()]
            skills_str = " / ".join(found_skills) if found_skills else "见详情"
            
            link = f"https://apply.careers.microsoft.com/careers/job/{job_id}"
            new_found.append(f"🚀 微软苏州新岗位：{title}\n🔑 核心技能：{skills_str}\n🔗 链接：{link}")
            visited.add(job_id)

    # 3. 推送逻辑（修改处：无论如何都说话）
    if new_found:
        report_text = f"【微软实习监控 - 发现更新】\n\n" + "\n\n".join(new_found)
        requests.post(webhook, json={"msg_type": "text", "content": {"text": report_text}})
        # 更新历史记录
        with open(history_file, "w") as f:
            f.write("\n".join(visited))
        print(f"已推送 {len(new_found)} 个新岗位。")
    else:
        # 这里是你要的：没发现新岗位也报平安
        safe_msg = f"✅ 微软监控报平安：已扫描官网，目前苏州共有 {total_count} 个实习岗位，暂无新增。"
        requests.post(webhook, json={"msg_type": "text", "content": {"text": safe_msg}})
        print("没有新岗位，已发送报平安消息。")

if __name__ == "__main__":
    main()
