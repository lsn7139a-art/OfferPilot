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
import json
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


def load_questions():
    """加载题库"""
    q_path = os.path.join(BASE_DIR, 'data', 'questions.json')
    with open(q_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, list):
        return {q['id']: q for q in data}
    return data


def create_daily_task():
    """为每道题创建独立的飞书待办任务"""
    config = load_config()
    feishu = config.get('feishu', {})
    user_open_id = feishu.get('user_open_id', '')

    if not user_open_id:
        print("⚠️ 未配置用户open_id，跳过创建待办")
        return False

    # 获取今日推送的题目ID
    log_path = os.path.join(BASE_DIR, 'data', 'daily_log.json')
    if not os.path.exists(log_path):
        print("⚠️ 无推送日志，跳过创建待办")
        return False
    with open(log_path, 'r', encoding='utf-8') as f:
        log = json.load(f)
    if not log:
        print("⚠️ 推送日志为空，跳过创建待办")
        return False
    latest = log[-1]
    question_ids = latest.get('question_ids', [])
    position_title = latest.get('position_title', '未知岗位')

    if not question_ids:
        print("⚠️ 今日无题目，跳过创建待办")
        return False

    # 加载题库详情
    questions_db = load_questions()

    # 截止时间：今天23:59:59
    from datetime import datetime, time
    today = datetime.now().strftime('%Y-%m-%d')
    today_end = datetime.combine(datetime.now().date(), time(23, 59, 59))
    due_timestamp = int(today_end.timestamp())

    # 公司名映射
    company_map = {
        'bytedance': '字节跳动', 'tencent': '腾讯', 'alibaba': '阿里巴巴',
        'meituan': '美团', 'huawei': '华为', 'xiaomi': '小米',
        'baidu': '百度', 'jd': '京东', 'netease': '网易', 'unitree': '宇树科技'
    }

    success_count = 0
    for i, qid in enumerate(question_ids, 1):
        q = questions_db.get(qid)
        if not q:
            print(f"⚠️ 题目 {qid} 不在题库中，跳过")
            continue

        category = q.get('category', '')
        subcategory = q.get('subcategory', '')
        title = q.get('title', '')
        difficulty = q.get('difficulty', '')
        companies = q.get('companies', [])
        leetcode_id = q.get('leetcode_id', '')
        source = q.get('source', '')
        source_url = q.get('source_url', '')
        description = q.get('description', '')

        # 任务标题：日期 + 第N题 + 【分类・子分类】+ 简短题目
        short_title = title if len(title) <= 30 else title[:27] + '...'
        cat_label = f"【{category}・{subcategory}】" if subcategory else f"【{category}】"
        summary = f"{today} 第{i}题 {cat_label} {short_title}"

        # 任务描述：完整题目内容 + 出处 + 公司 + 难度
        desc_lines = [
            f"📅 {today} | 💼 关联岗位：{position_title}",
            f"",
            f"📝 {title}",
            f"",
        ]
        if description:
            desc_lines.append(description)
            desc_lines.append("")

        # 元信息
        meta_parts = []
        if difficulty:
            diff_map = {'easy': '简单', 'medium': '中等', 'hard': '困难'}
            meta_parts.append(f"难度：{diff_map.get(difficulty, difficulty)}")
        if companies:
            company_names = [company_map.get(c, c) for c in companies]
            meta_parts.append(f"出现于：{'、'.join(company_names[:5])}")
        if leetcode_id:
            meta_parts.append(f"LeetCode {leetcode_id}")
        if source:
            meta_parts.append(f"来源：{source}")
        if source_url:
            meta_parts.append(f"🔗 {source_url}")

        if meta_parts:
            desc_lines.append(" | ".join(meta_parts))
            desc_lines.append("")

        desc_lines.append("💬 回复「答案{}」查看本题解析".format(i))
        description_text = '\n'.join(desc_lines)

        try:
            task_guid = create_task(summary, description_text, user_open_id, due_timestamp)
            print(f"✅ 第{i}题待办创建成功：{short_title} (guid: {task_guid})")
            success_count += 1
        except Exception as e:
            print(f"❌ 第{i}题待办创建失败：{e}")

    print(f"\n📊 共创建 {success_count}/{len(question_ids)} 个待办任务")
    return success_count > 0


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
