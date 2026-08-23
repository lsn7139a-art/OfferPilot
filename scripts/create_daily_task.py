#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建每日飞书任务（待办提醒）
- 任务标题：日期 + 面试题打卡 + 今日岗位
- 任务描述：岗位摘要 + 3道题标题 + 引导看群消息
- 任务负责人：当前用户
- 截止时间：当天
"""

import json
import os
import subprocess
import sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 用户open_id（从config或硬编码）
USER_OPEN_ID = "ou_5d30d2e8b5989553fae923990b1dfdf7"


def load_json(filepath):
    full_path = os.path.join(BASE_DIR, filepath)
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_today_date():
    return datetime.now().strftime('%Y-%m-%d')


def get_weekday_cn():
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return weekdays[datetime.now().weekday()]


def get_latest_daily_info():
    """从最近一次推送日志中获取今日岗位和题目信息"""
    log_path = os.path.join(BASE_DIR, 'data', 'daily_log.json')
    if not os.path.exists(log_path):
        return None, []

    with open(log_path, 'r', encoding='utf-8') as f:
        log = json.load(f)

    if not log:
        return None, []

    latest = log[-1]
    position_title = latest.get('position_title', '未知岗位')
    question_titles = latest.get('question_titles', [])
    return position_title, question_titles


def get_position_url():
    """从最近一次推送中获取岗位链接"""
    log_path = os.path.join(BASE_DIR, 'data', 'daily_log.json')
    if not os.path.exists(log_path):
        return ''

    with open(log_path, 'r', encoding='utf-8') as f:
        log = json.load(f)

    if not log:
        return ''

    latest = log[-1]
    position_id = latest.get('position_id', '')

    # 从positions.json中找对应的url
    positions_data = load_json('data/positions.json')
    for p in positions_data.get('positions', []):
        if p['id'] == position_id:
            return p.get('url', '')
    return ''


def create_task(summary, description, due_date):
    """调用lark-cli创建飞书任务"""
    cmd = [
        'lark-cli', 'task', '+create',
        '--summary', summary,
        '--description', description,
        '--assignee', USER_OPEN_ID,
        '--due', due_date,
    ]

    print(f"创建任务：{summary}")
    print(f"截止时间：{due_date}")
    print()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        if result.returncode == 0:
            # 解析返回的JSON，提取任务链接
            try:
                output = json.loads(result.stdout)
                if output.get('ok'):
                    task_url = output.get('data', {}).get('url', '')
                    task_guid = output.get('data', {}).get('guid', '')
                    print(f"\n✅ 飞书任务创建成功！")
                    print(f"   任务GUID: {task_guid}")
                    print(f"   任务链接: {task_url}")
                    return True, task_url
            except json.JSONDecodeError:
                pass
            print("\n✅ 任务创建命令执行成功（返回格式可能非标准JSON）")
            return True, ''
        else:
            print(f"\n❌ 任务创建失败，返回码: {result.returncode}")
            return False, ''
    except Exception as e:
        print(f"\n❌ 创建任务时出错: {e}")
        return False, ''


def main():
    today = get_today_date()
    weekday = get_weekday_cn()

    # 获取今日岗位和题目信息
    position_title, question_titles = get_latest_daily_info()
    position_url = get_position_url()

    if not position_title:
        print("⚠️ 未找到今日推送记录，请先运行 daily_push.py 生成推送内容")
        return

    # 任务标题
    summary = f"{today} 面试题打卡 - {position_title}"

    # 任务描述
    desc_lines = []
    desc_lines.append(f"📅 {today} {weekday}")
    desc_lines.append(f"💼 今日岗位：{position_title}")
    if position_url:
        desc_lines.append(f"🔗 岗位链接：{position_url}")
    desc_lines.append("")
    desc_lines.append("📝 今日题目：")
    for i, title in enumerate(question_titles, 1):
        # 截断过长的题目标题
        if len(title) > 50:
            title = title[:47] + "..."
        desc_lines.append(f"   {i}. {title}")
    desc_lines.append("")
    desc_lines.append("💬 详细内容（完整题目+答案解析）见飞书群「面试题每日打卡」")
    desc_lines.append("")
    desc_lines.append("📌 回复指令：")
    desc_lines.append("   「答案1」→ 查看第1题解析")
    desc_lines.append("   「完成1,2」→ 标记进度")
    desc_lines.append("   「查看进度」→ 查看统计")

    description = '\n'.join(desc_lines)

    # 创建任务
    success, task_url = create_task(summary, description, today)

    if success:
        print(f"\n✅ 每日待办任务已创建，你可以在飞书任务中心查看")
        if task_url:
            print(f"   直接打开：{task_url}")
    else:
        print("\n❌ 任务创建失败，请检查lark-cli配置和权限")
        sys.exit(1)


if __name__ == '__main__':
    main()
