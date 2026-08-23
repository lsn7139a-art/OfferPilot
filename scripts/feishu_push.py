#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书推送脚本
- 调用daily_push.py生成每日题目
- 通过lark-cli发送到飞书群聊
- 处理多行文本，避免Shell解析问题
"""

import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 飞书群聊ID（面试题每日打卡）
FEISHU_CHAT_ID = "oc_839d3dac5ee30f5f118c66b8f5793539"


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
    # 输出中包含消息和最后的状态行，需要提取消息部分
    output = result.stdout
    # 找到消息结束标记（最后一个"="分隔线后是说明）
    lines = output.split('\n')
    message_lines = []
    in_message = False
    for line in lines:
        if line.startswith('📅'):
            in_message = True
        if in_message:
            message_lines.append(line)
        # 消息以回复格式说明结束
        if '查看进度' in line and in_message:
            break
    return '\n'.join(message_lines) if message_lines else output


def send_to_feishu(message, chat_id=None):
    """通过lark-cli发送消息到飞书"""
    if chat_id is None:
        chat_id = FEISHU_CHAT_ID

    if not message:
        print("消息内容为空，跳过发送")
        return False

    cmd = [
        'lark-cli', 'im', '+messages-send',
        '--chat-id', chat_id,
        '--text', message,
        '--as', 'user'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        if result.returncode == 0:
            print("✅ 飞书消息发送成功")
            print(result.stdout)
            return True
        else:
            print(f"❌ 飞书消息发送失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False


def send_evening_reminder():
    """发送晚间提醒"""
    message = (
        "🌙 晚间学习提醒\n"
        "━━━━━━━━━━━━━━━\n"
        "今天的面试题完成了吗？\n\n"
        "回复进度格式：\n"
        "  \"完成1,2 第3题不会\"\n"
        "  \"查看进度\"\n\n"
        "坚持每天打卡，offer就在眼前！💪"
    )
    return send_to_feishu(message)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='飞书推送脚本')
    parser.add_argument('--mode', choices=['daily', 'evening', 'test'], default='daily',
                        help='推送模式: daily=每日题目, evening=晚间提醒, test=测试消息')
    parser.add_argument('--chat-id', default=None, help='飞书群聊ID')
    args = parser.parse_args()

    if args.mode == 'daily':
        print("📝 生成每日题目...")
        message = generate_daily_message()
        if message:
            send_to_feishu(message, args.chat_id)
            # 同时创建飞书待办任务
            print("\n📋 创建飞书每日待办任务...")
            task_script = os.path.join(BASE_DIR, 'scripts', 'create_daily_task.py')
            task_result = subprocess.run(
                [sys.executable, task_script],
                capture_output=True,
                text=True,
                encoding='utf-8',
                cwd=BASE_DIR
            )
            print(task_result.stdout)
            if task_result.stderr:
                print(task_result.stderr)
            if task_result.returncode == 0:
                print("✅ 飞书待办任务创建成功")
            else:
                print("⚠️ 飞书待办任务创建失败（不影响群消息推送）")
    elif args.mode == 'evening':
        print("🌙 发送晚间提醒...")
        send_evening_reminder()
    elif args.mode == 'test':
        message = "🧪 测试消息：飞书推送系统运行正常"
        send_to_feishu(message, args.chat_id)


if __name__ == '__main__':
    main()
