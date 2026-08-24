#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书推送脚本（直接调API版，不依赖lark-cli）
- 每日推送：1个岗位 + 3道题
- 昨日未完成的题目 → 延期继续做（更新截止日期）
- 昨日已完成的题目 → 替换成新题
- 每道题一个独立飞书待办
- 自动检测飞书待办完成状态
"""

import subprocess
import sys
import os
import json
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

from feishu_api import (
    send_message_to_chat, create_task, get_task_status,
    update_task_due, load_config
)


def load_json(filepath):
    full_path = os.path.join(BASE_DIR, filepath)
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    full_path = os.path.join(BASE_DIR, filepath)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_questions():
    """加载题库，返回 {id: question}"""
    data = load_json('data/questions.json')
    if isinstance(data, list):
        return {q['id']: q for q in data}
    return data


def check_yesterday_progress():
    """
    检查昨日推送任务的完成状态
    返回: (unfinished_list, finished_qids, yesterday_entry)
      unfinished_list: [(qid, guid), ...] 未完成的题目及旧任务guid
      finished_qids: [qid, ...] 已完成的题目ID
      yesterday_entry: 昨日推送记录（或None）
    """
    log_path = os.path.join(BASE_DIR, 'data', 'daily_log.json')
    if not os.path.exists(log_path):
        return [], [], None

    with open(log_path, 'r', encoding='utf-8') as f:
        log = json.load(f)

    if not log:
        return [], [], None

    # 找最近一条有task_guids的记录
    latest = None
    for entry in reversed(log):
        if entry.get('task_guids'):
            latest = entry
            break

    if not latest:
        return [], [], None

    question_ids = latest.get('question_ids', [])
    task_guids = latest.get('task_guids', [])

    if len(question_ids) != len(task_guids):
        print(f"⚠️ 题目数({len(question_ids)})与任务数({len(task_guids)})不匹配，按新题处理")
        return [], [], latest

    unfinished = []
    finished = []
    for qid, guid in zip(question_ids, task_guids):
        if not guid:
            finished.append(qid)
            continue
        status = get_task_status(guid)
        if status == 'done':
            finished.append(qid)
        else:
            unfinished.append((qid, guid))

    print(f"📊 昨日任务：完成 {len(finished)}/{len(question_ids)}，未完成 {len(unfinished)}")
    return unfinished, finished, latest


def select_new_questions(questions_db, exclude_ids, count, position, progress):
    """
    从题库中选新题（排除指定ID）
    """
    from daily_push import select_questions
    questions_list = list(questions_db.values())
    # 临时把排除的题标记为已完成，让select_questions排除它们
    progress_copy = json.loads(json.dumps(progress))
    if 'completed' not in progress_copy:
        progress_copy['completed'] = []
    progress_copy['completed'].extend(exclude_ids)
    config = load_json('config.json')
    return select_questions(questions_list, progress_copy, config, position, count)


def generate_daily_message():
    """
    生成每日题目消息：
    - 昨日未完成的题目 → 保留（延期）
    - 昨日已完成的题目 → 替换成新题
    - 保证每天3道
    - 岗位每天换新
    返回: (message, question_ids, position, old_task_map)
      old_task_map: {qid: old_guid} 昨日未完成题目的旧任务guid
    """
    from daily_push import (
        format_daily_message, log_daily_push, select_position
    )

    # 检查昨日进度
    unfinished, finished_qids, yesterday = check_yesterday_progress()

    positions_data = load_json('data/positions.json')
    positions = positions_data.get('positions', [])
    progress = load_json('data/progress.json')
    companies_data = load_json('data/companies.json')
    questions_db = load_questions()

    daily_count = load_json('config.json').get('question_selection', {}).get('daily_count', 3)

    # 选新岗位（每天换）
    position = select_position(positions, progress)
    print(f"💼 今日岗位：{position['company_name']}・{position['title']}")

    # 确定今日题目
    old_task_map = {}  # qid -> old_guid
    today_question_ids = []

    if unfinished:
        # 保留未完成的题目
        for qid, guid in unfinished:
            today_question_ids.append(qid)
            old_task_map[qid] = guid
        print(f"🔄 保留 {len(unfinished)} 道未完成题目（延期）")

    # 需要补充的新题数量
    need_new = daily_count - len(today_question_ids)
    if need_new > 0:
        # 排除已完成和未完成的，选新题
        exclude = set(finished_qids) | set(today_question_ids)
        new_questions = select_new_questions(questions_db, list(exclude), need_new, position, progress)
        for q in new_questions:
            today_question_ids.append(q['id'])
        print(f"🆕 补充 {len(new_questions)} 道新题")

    # 确保题目顺序稳定
    today_question_ids = today_question_ids[:daily_count]

    # 生成消息
    selected = [questions_db[qid] for qid in today_question_ids if qid in questions_db]
    message = format_daily_message(position, selected, progress, companies_data)

    # 记录日志
    log_daily_push(position, selected)

    return message, today_question_ids, position, old_task_map


def create_daily_tasks(question_ids, position_title, old_task_map=None):
    """
    为每道题处理飞书待办：
    - 旧题（昨日未完成）→ 更新截止日期到今天结束（延期）
    - 新题 → 创建新任务
    返回: task_guids列表（与question_ids顺序对应）
    """
    if old_task_map is None:
        old_task_map = {}

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

        # 判断是旧题还是新题
        if qid in old_task_map:
            # 旧题：更新截止日期（延期）
            old_guid = old_task_map[qid]
            try:
                update_task_due(old_guid, due_timestamp)
                print(f"🔄 第{i}题延期成功（更新截止日期）：{short_title}")
                task_guids.append(old_guid)
            except Exception as e:
                print(f"❌ 第{i}题延期失败，尝试新建：{e}")
                # 延期失败则新建
                summary = f"{today} 第{i}题 {cat_label} {short_title}"
                desc = _build_task_desc(today, position_title, title, description, difficulty,
                                         companies, leetcode_id, source, source_url, company_map, i)
                try:
                    new_guid = create_task(summary, desc, user_open_id, due_timestamp)
                    print(f"   ✅ 新建成功：{short_title}")
                    task_guids.append(new_guid)
                except Exception as e2:
                    print(f"   ❌ 新建也失败：{e2}")
                    task_guids.append('')
        else:
            # 新题：创建新任务
            summary = f"{today} 第{i}题 {cat_label} {short_title}"
            desc = _build_task_desc(today, position_title, title, description, difficulty,
                                     companies, leetcode_id, source, source_url, company_map, i)
            try:
                new_guid = create_task(summary, desc, user_open_id, due_timestamp)
                print(f"✅ 第{i}题新建成功：{short_title}")
                task_guids.append(new_guid)
            except Exception as e:
                print(f"❌ 第{i}题新建失败：{e}")
                task_guids.append('')

    valid = len([g for g in task_guids if g])
    print(f"\n📊 待办处理完成：{valid}/{len(question_ids)} 个有效")
    return task_guids


def _build_task_desc(today, position_title, title, description, difficulty,
                     companies, leetcode_id, source, source_url, company_map, idx):
    """构建任务描述"""
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

    desc_lines.append(f"💬 回复「答案{idx}」查看本题解析")
    return '\n'.join(desc_lines)


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
        "未完成的题目明天会自动延期继续做\n\n"
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
        print("📝 生成每日题目（含昨日进度检测+延期逻辑）...")
        message, question_ids, position, old_task_map = generate_daily_message()

        if message:
            send_to_feishu(message, args.chat_id)

            print("\n📋 处理飞书待办（旧题延期+新题创建）...")
            position_title = f"{position['company_name']}・{position['title']}" if position else "未知岗位"
            task_guids = create_daily_tasks(question_ids, position_title, old_task_map)

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
