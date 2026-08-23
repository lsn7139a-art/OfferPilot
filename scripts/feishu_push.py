#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书推送脚本（直接调API版，不依赖lark-cli）
- 调用daily_push.py生成每日题目
- 通过飞书API发送到群聊
- 同时创建飞书待办任务
"""

import subprocess
import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

from feishu_api import send_message_to_chat, create_task, load_config


def generate_daily_message():
    """运行daily_push.py生成每日题目消息"""
    script_path = os.path.join(BASE_DIR, 'scripts', 'daily_push.py')
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        cwd=BASE_DIR
    )
    if result.returncode != 0:
        print(f"生成每日题目失败: {result.stderr}")
        return None
    output = result.stdout
    # 提取消息部分（从日期行开始，到回复指令结束）
    lines = output.split('\n')
    message_lines = []
    in_message = False
    for line in lines:
        # 消息以日期开头
        if any(line.startswith(f"20{y}") for y in range(20, 30)) and '・' in line:
            in_message = True
        if in_message:
            message_lines.append(line)
        # 消息以"查看进度"结束
        if '查看进度' in line and in_message:
            break
    return '\n'.join(message_lines) if message_lines else output


def get_position_info():
    """从最近推送日志中获取今日岗位信息"""
    log_path = os.path.join(BASE_DIR, 'data', 'daily_log.json')
    if not os.path.exists(log_path):
        return "未知岗位", []
    import json
    with open(log_path, 'r', encoding='utf-8') as f:
        log = json.load(f)
    if not log:
        return "未知岗位", []
    latest = log[-1]
    return latest.get('position_title', '未知岗位'), latest.get('question_titles', [])


def send_to_feishu(message, chat_id=None):
    """通过飞书API发送消息到群"""
    config = load_config()
    if chat_id is None:
        chat_id = config.get('feishu', {}).get('chat_id', '')

    if not message:
        print("消息内容为空，跳过发送")
        return False

    try:
        msg_id = send_message_to_chat(chat_id, message)
        print(f"✅ 飞书消息发送成功，message_id: {msg_id}")
        return True
    except Exception as e:
        print(f"❌ 飞书消息发送失败: {e}")
        return False


def create_daily_task():
    """创建每日飞书待办任务"""
    config = load_config()
    feishu = config.get('feishu', {})
    user_open_id = feishu.get('user_open_id', '')

    if not user_open_id:
        print("⚠️ 未配置用户open_id，跳过创建待办")
        return False

    position_title, question_titles = get_position_info()

    # 任务标题
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    summary = f"{today} 面试题打卡 - {position_title}"

    # 任务描述
    desc_lines = [
        f"📅 {today}",
        f"💼 今日岗位：{position_title}",
        "",
        "📝 今日题目："
    ]
    for i, title in enumerate(question_titles, 1):
        if len(title) > 50:
            title = title[:47] + "..."
        desc_lines.append(f"   {i}. {title}")
    desc_lines.extend([
        "",
        "💬 详细内容见飞书群「lsn」",
        "",
        "📌 回复指令：",
        "   「答案1」→ 查看第1题解析",
        "   「完成1,2」→ 标记进度",
        "   「查看进度」→ 查看统计"
    ])
    description = '\n'.join(desc_lines)

    # 截止时间：今天结束
    import time
    due_timestamp = int(time.time()) + 86400  # 明天

    try:
        task_guid = create_task(summary, description, user_open_id, due_timestamp)
        print(f"✅ 飞书待办任务创建成功，guid: {task_guid}")
        return True
    except Exception as e:
        print(f"❌ 飞书待办任务创建失败: {e}")
        return False


def send_evening_reminder():
    """发送晚间提醒"""
    config = load_config()
    chat_id = config.get('feishu', {}).get('chat_id', '')
    message = (
        "🌙 晚间学习提醒\n"
        "━━━━━━━━━━━━━━━\n"
        "今天的面试题完成了吗？\n\n"
        "回复进度格式：\n"
        "  \"完成1,2 第3题不会\"\n"
        "  \"查看进度\"\n\n"
        "坚持每天打卡，offer就在眼前！💪"
    )
    return send_to_feishu(message, chat_id)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='飞书推送脚本')
    parser.add_argument('--mode', choices=['daily', 'evening', 'test'], default='daily',
                        help='推送模式: daily=每日题目+待办, evening=晚间提醒, test=测试消息')
    parser.add_argument('--chat-id', default=None, help='飞书群聊ID')
    args = parser.parse_args()

    if args.mode == 'daily':
        print("📝 生成每日题目...")
        message = generate_daily_message()
        if message:
            send_to_feishu(message, args.chat_id)
            print("\n📋 创建飞书每日待办任务...")
            create_daily_task()
    elif args.mode == 'evening':
        print("🌙 发送晚间提醒...")
        send_evening_reminder()
    elif args.mode == 'test':
        message = "🧪 测试消息：OfferPilot 飞书推送系统运行正常"
        send_to_feishu(message, args.chat_id)


if __name__ == '__main__':
    main()
