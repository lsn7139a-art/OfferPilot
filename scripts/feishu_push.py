#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书推送脚本（直接调API版，不依赖lark-cli）
- 调用daily_push.py生成每日题目
- 通过飞书API发送到群聊
- 每道题创建独立的飞书待办任务
- 检测昨日任务完成状态，未完成则继续做旧题+只换岗位
"""

import subprocess
import sys
import os
import json
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

from feishu_api import send_message_to_chat, create_task, get_task_status, load_config


def load_json(filepath):
    full_path = os.path.join(BASE_DIR, filepath)
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    full_path = os.path.join(BASE_DIR, filepath)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_questions():
    """加载题库"""
    data = load_json('data/questions.json')
    if isinstance(data, list):
        return {q['id']: q for q in data}
    return data


def check_yesterday_progress():
    """
    检查昨日推送任务的完成状态
    返回: (未完成的题目ID列表, 昨日推送记录)
    """
    log_path = os.path.join(BASE_DIR, 'data', 'daily_log.json')
    if not os.path.exists(log_path):
        return [], None

    with open(log_path, 'r', encoding='utf-8') as f:
        log = json.load(f)

    if not log:
        return [], None

    # 找最近一条有task_guids的记录
    latest = None
    for entry in reversed(log):
        if entry.get('task_guids'):
            latest = entry
            break

    if not latest:
        return [], None

    question_ids = latest.get('question_ids', [])
    task_guids = latest.get('task_guids', [])

    if len(question_ids) != len(task_guids):
        print(f"⚠️ 题目数({len(question_ids)})与任务数({len(task_guids)})不匹配，按新题处理")
        return [], latest

    unfinished = []
    finished = []
    for qid, guid in zip(question_ids, task_guids):
        status = get_task_status(guid)
        if status == 'done':
            finished.append(qid)
        else:
            unfinished.append(qid)

    print(f"📊 昨日任务状态：完成 {len(finished)}/{len(question_ids)}，未完成 {len(unfinished)}")
    return unfinished, latest


def generate_message_with_questions(question_ids, position, progress, companies_data):
    """用指定题目+岗位生成推送消息（复用daily_push的格式化逻辑）"""
    sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))
    from daily_push import format_daily_message

    questions_db = load_questions()
    selected = [questions_db[qid] for qid in question_ids if qid in questions_db]
    return format_daily_message(position, selected, progress, companies_data)


def select_new_position(positions, progress):
    """选择一个新岗位（不重复最近7天的）"""
    sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))
    from daily_push import select_position
    return select_position(positions, progress)


def generate_daily_message():
    """
    生成每日题目消息：
    - 先检查昨日任务完成状态
    - 有未完成的 → 继续用旧题，只换岗位
    - 全部完成 → 调用daily_push.py生成新题
    返回: (消息文本, 题目ID列表, 岗位对象)
    """
    # 检查昨日进度
    unfinished, yesterday = check_yesterday_progress()

    positions_data = load_json('data/positions.json')
    positions = positions_data.get('positions', [])
    progress = load_json('data/progress.json')
    companies_data = load_json('data/companies.json')

    if unfinished and positions:
        # 有未完成的题目，继续做，只换岗位
        print(f"🔄 检测到 {len(unfinished)} 道未完成题目，继续做旧题，只换岗位")

        # 选一个新岗位
        position = select_new_position(positions, progress)

        # 用旧题+新岗位生成消息
        message = generate_message_with_questions(unfinished, position, progress, companies_data)

        # 记录日志（和daily_push的log_daily_push类似，但用旧题）
        from daily_push import log_daily_push
        questions_db = load_questions()
        selected = [questions_db[qid] for qid in unfinished if qid in questions_db]
        log_daily_push(position, selected)

        return message, unfinished, position
    else:
        # 全部完成或无历史记录，生成新题
        print("✅ 昨日任务全部完成，生成新题目")
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
            return None, [], None

        output = result.stdout
        # 提取消息部分
        lines = output.split('\n')
        message_lines = []
        in_message = False
        for line in lines:
            if any(line.startswith(f"20{y}") for y in range(20, 30)) and '・' in line:
                in_message = True
            if in_message:
                message_lines.append(line)
            if '查看进度' in line and in_message:
                break
        message = '\n'.join(message_lines) if message_lines else output

        # 从日志获取今日题目ID
        log = load_json('data/daily_log.json')
        latest = log[-1] if log else {}
        question_ids = latest.get('question_ids', [])

        # 获取岗位对象
        position_id = latest.get('position_id', '')
        position = next((p for p in positions if p['id'] == position_id), None)

        return message, question_ids, position


def create_daily_tasks(question_ids, position_title):
    """
    为每道题创建独立的飞书待办任务
    返回: 任务guid列表
    """
    config = load_config()
    feishu = config.get('feishu', {})
    user_open_id = feishu.get('user_open_id', '')

    if not user_open_id:
        print("⚠️ 未配置用户open_id，跳过创建待办")
        return []

    if not question_ids:
        print("⚠️ 无题目，跳过创建待办")
        return []

    questions_db = load_questions()

    # 截止时间：今天23:59:59
    from datetime import datetime, time
    today = datetime.now().strftime('%Y-%m-%d')
    today_end = datetime.combine(datetime.now().date(), time(23, 59, 59))
    due_timestamp = int(today_end.timestamp())

    company_map = {
        'bytedance': '字节跳动', 'tencent': '腾讯', 'alibaba': '阿里巴巴',
        'meituan': '美团', 'huawei': '华为', 'xiaomi': '小米',
        'baidu': '百度', 'jd': '京东', 'netease': '网易', 'unitree': '宇树科技'
    }

    task_guids = []
    for i, qid in enumerate(question_ids, 1):
        q = questions_db.get(qid)
        if not q:
            print(f"⚠️ 题目 {qid} 不在题库中，跳过")
            task_guids.append('')
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

        short_title = title if len(title) <= 30 else title[:27] + '...'
        cat_label = f"【{category}・{subcategory}】" if subcategory else f"【{category}】"
        summary = f"{today} 第{i}题 {cat_label} {short_title}"

        desc_lines = [
            f"📅 {today} | 💼 关联岗位：{position_title}",
            "",
            f"📝 {title}",
            "",
        ]
        if description:
            desc_lines.append(description)
            desc_lines.append("")

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

        desc_lines.append(f"💬 回复「答案{i}」查看本题解析")
        description_text = '\n'.join(desc_lines)

        try:
            task_guid = create_task(summary, description_text, user_open_id, due_timestamp)
            print(f"✅ 第{i}题待办创建成功：{short_title}")
            task_guids.append(task_guid)
        except Exception as e:
            print(f"❌ 第{i}题待办创建失败：{e}")
            task_guids.append('')

    print(f"\n📊 共创建 {len([g for g in task_guids if g])}/{len(question_ids)} 个待办任务")
    return task_guids


def save_task_guids_to_log(task_guids):
    """把任务guids回填到今日推送日志"""
    log_path = os.path.join(BASE_DIR, 'data', 'daily_log.json')
    if not os.path.exists(log_path):
        return
    with open(log_path, 'r', encoding='utf-8') as f:
        log = json.load(f)
    if not log:
        return
    log[-1]['task_guids'] = task_guids
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print("📝 任务guids已回填到推送日志")


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


def send_evening_reminder():
    """发送晚间提醒"""
    config = load_config()
    chat_id = config.get('feishu', {}).get('chat_id', '')
    message = (
        "🌙 晚间学习提醒\n"
        "━━━━━━━━━━━━━━━\n"
        "今天的面试题完成了吗？\n\n"
        "在飞书待办里点「完成」即可，系统自动检测进度\n"
        "也可以在群里回复：\n"
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
        print("📝 生成每日题目（含昨日进度检测）...")
        message, question_ids, position = generate_daily_message()

        if message:
            send_to_feishu(message, args.chat_id)

            print("\n📋 创建飞书每日待办任务（每题独立）...")
            position_title = f"{position['company_name']}・{position['title']}" if position else "未知岗位"
            task_guids = create_daily_tasks(question_ids, position_title)

            if task_guids:
                save_task_guids_to_log(task_guids)
    elif args.mode == 'evening':
        print("🌙 发送晚间提醒...")
        send_evening_reminder()
    elif args.mode == 'test':
        message = "🧪 测试消息：OfferPilot 飞书推送系统运行正常"
        send_to_feishu(message, args.chat_id)


if __name__ == '__main__':
    main()
