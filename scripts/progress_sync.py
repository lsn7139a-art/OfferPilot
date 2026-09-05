#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进度同步Agent
- 解析用户回复的进度消息
- 更新progress.json
- 支持的指令格式：
  "完成1,2,3" / "1,2 done" / "做完了1和2"
  "第3题不会" / "3 skip" / "跳过3"
  "进行中2" / "2 in progress"
  "查看进度" / "统计" / "status"
  "复习算法" / "切换到操作系统"
  "目标公司 字节,宇树"
"""

import json
import os
import re
from datetime import datetime
from collections import Counter
from time_utils import get_today_date, get_now, set_timezone
from task_rollover import record_message_outcomes

# 确保时区为北京时间
set_timezone()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(filepath):
    full_path = os.path.join(BASE_DIR, filepath)
    with open(full_path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def save_json(filepath, data):
    full_path = os.path.join(BASE_DIR, filepath)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_numbers(text):
    """从文本中提取数字（支持中文数字）"""
    # 先提取阿拉伯数字
    nums = re.findall(r'\d+', text)
    result = [int(n) for n in nums]

    # 中文数字映射
    cn_num_map = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '两': 2
    }
    for cn, num in cn_num_map.items():
        if cn in text and num not in result:
            result.append(num)

    return sorted(set(result))


def parse_progress_message(message, daily_questions):
    """
    解析用户进度消息
    返回: dict with actions
    """
    msg = message.strip().lower()
    actions = {
        'completed': [],
        'skipped': [],
        'in_progress': [],
        'query': None,
        'query_answer': [],
        'switch_category': None,
        'set_target_companies': None,
        'unknown': False
    }

    # 查询答案："第2题答案" "答案1,2" "给我第3题答案"
    if '答案' in msg or '解析' in msg or '解答' in msg:
        # 匹配 "第X题答案" "答案X" "X题答案"
        patterns = [
            r'第\s*(\d+)\s*题\s*(?:的)?\s*(?:答案|解析|解答)',
            r'(?:答案|解析|解答)\s*[:：]?\s*([\d,，、\s]+)',
            r'([\d,，、\s]+)\s*(?:题)?\s*(?:的)?\s*(?:答案|解析|解答)',
            r'给我\s*第?\s*(\d+)\s*题?\s*(?:的)?\s*(?:答案|解析|解答)',
        ]
        for pattern in patterns:
            match = re.search(pattern, msg)
            if match:
                nums = parse_numbers(match.group(1))
                actions['query_answer'].extend(nums)
        if not actions['query_answer']:
            # 没匹配到具体题号，默认查所有今日题目
            actions['query_answer'] = [1, 2, 3]
        actions['query_answer'] = list(set(actions['query_answer']))
        return actions

    # 查看进度
    if any(kw in msg for kw in ['查看进度', '统计', 'status', '进度', '怎么样了', '完成了多少']):
        actions['query'] = 'progress'
        return actions

    # 切换复习方向
    category_match = re.search(r'(?:复习|切换|学|主攻)\s*(算法|操作系统|计算机网络|网络|数据库|c\+\+|cpp|java|python|系统设计|具身智能|机器人|ai大模型|大模型|ai)', msg)
    if category_match:
        cat = category_match.group(1)
        cat_map = {
            '算法': '算法', '操作系统': '操作系统',
            '计算机网络': '计算机网络', '网络': '计算机网络',
            '数据库': '数据库', 'c++': 'C++', 'cpp': 'C++',
            'java': 'Java', 'python': 'Python',
            '系统设计': '系统设计', '具身智能': '具身智能',
            '机器人': '具身智能', 'ai大模型': 'AI大模型',
            '大模型': 'AI大模型', 'ai': 'AI大模型'
        }
        actions['switch_category'] = cat_map.get(cat, cat)
        return actions

    # 设置目标公司
    if '目标公司' in msg or '目标' in msg:
        company_map = {
            '字节': 'bytedance', '字节跳动': 'bytedance', 'bytedance': 'bytedance',
            '腾讯': 'tencent', 'tencent': 'tencent', '鹅厂': 'tencent',
            '阿里': 'alibaba', '阿里巴巴': 'alibaba', 'alibaba': 'alibaba',
            '美团': 'meituan', 'meituan': 'meituan',
            '华为': 'huawei', 'huawei': 'huawei',
            '小米': 'xiaomi', 'xiaomi': 'xiaomi',
            '百度': 'baidu', 'baidu': 'baidu',
            '宇树': 'unitree', '宇树科技': 'unitree', 'unitree': 'unitree'
        }
        companies = []
        for cn, cid in company_map.items():
            if cn in msg:
                companies.append(cid)
        if companies:
            actions['set_target_companies'] = list(set(companies))
            return actions

    # 解析完成/跳过/进行中
    # 匹配 "完成X" "做完了X" "X done" "X完成"
    completed_patterns = [
        r'(?:完成|做完|搞定|会了|掌握|done|finish|ok|✅|✓)\s*([\d,，、\s]+)',
        r'([\d,，、\s]+)\s*(?:完成|做完|搞定|会了|done|finish)',
    ]
    for pattern in completed_patterns:
        match = re.search(pattern, msg)
        if match:
            nums = parse_numbers(match.group(1))
            actions['completed'].extend(nums)

    # 匹配 "跳过X" "X不会" "X skip" "X太难"
    skip_patterns = [
        r'(?:跳过|不会|太难|不懂|skip|pass|❌|✗)\s*([\d,，、\s]+)',
        r'([\d,，、\s]+)\s*(?:不会|跳过|太难|不懂|skip|pass)',
        r'第\s*(\d+)\s*题\s*(?:不会|跳过|太难|不懂)',
    ]
    for pattern in skip_patterns:
        match = re.search(pattern, msg)
        if match:
            nums = parse_numbers(match.group(1))
            actions['skipped'].extend(nums)

    # 匹配 "进行中X" "X在做" "X ing"
    in_progress_patterns = [
        r'(?:进行中|在做|正在做|ing|wip)\s*([\d,，、\s]+)',
        r'([\d,，、\s]+)\s*(?:进行中|在做|正在做|ing)',
    ]
    for pattern in in_progress_patterns:
        match = re.search(pattern, msg)
        if match:
            nums = parse_numbers(match.group(1))
            actions['in_progress'].extend(nums)

    # 如果没有匹配到任何模式，但消息中有数字，默认当作完成
    if not actions['completed'] and not actions['skipped'] and not actions['in_progress']:
        nums = parse_numbers(msg)
        if nums and any(kw in msg for kw in ['题', '道', '个', '完成', '做', '答']):
            actions['completed'].extend(nums)
        elif nums:
            actions['completed'].extend(nums)  # 纯数字默认完成

    # 去重
    actions['completed'] = list(set(actions['completed']))
    actions['skipped'] = list(set(actions['skipped']))
    actions['in_progress'] = list(set(actions['in_progress']))

    if not any([actions['completed'], actions['skipped'], actions['in_progress'],
                actions['query'], actions['switch_category'], actions['set_target_companies']]):
        actions['unknown'] = True

    return actions


def map_numbers_to_question_ids(numbers, daily_questions):
    """将题号（1,2,3）映射为实际的question_id"""
    ids = []
    for n in numbers:
        if 1 <= n <= len(daily_questions):
            ids.append(daily_questions[n - 1]['id'])
    return ids


def get_today_questions():
    """获取今日推送的题目"""
    log_path = os.path.join(BASE_DIR, 'data', 'daily_log.json')
    if not os.path.exists(log_path):
        return []

    with open(log_path, 'r', encoding='utf-8-sig') as f:
        log = json.load(f)

    today = get_today_date()
    today_entries = [e for e in log if e.get('date') == today]
    if not today_entries:
        return []

    # 取今天最后一次推送
    latest = today_entries[-1]
    question_ids = latest.get('question_ids', [])

    # 从题库中查找
    questions_data = load_json('data/questions.json')
    q_map = {q['id']: q for q in (questions_data if isinstance(questions_data, list) else questions_data.get('questions', []))}
    return [q_map[qid] for qid in question_ids if qid in q_map]


def update_progress(actions):
    """根据actions更新progress.json"""
    progress = load_json('data/progress.json')
    today = get_today_date()
    daily_questions = get_today_questions()

    response_parts = []

    # 查询进度
    if actions.get('query') == 'progress':
        total = progress.get('total_questions', 0)
        completed = len(progress.get('completed', []))
        skipped = len(progress.get('skipped', []))
        in_progress = len(progress.get('in_progress', []))
        streak = progress.get('streak', 0)

        # 分类统计
        questions_data = load_json('data/questions.json')
        q_map = {q['id']: q for q in (questions_data if isinstance(questions_data, list) else questions_data.get('questions', []))}
        completed_cats = Counter()
        for qid in progress.get('completed', []):
            if qid in q_map:
                completed_cats[q_map[qid]['category']] += 1

        msg = f"📊 学习进度统计\n"
        msg += f"━━━━━━━━━━━━━━━\n"
        msg += f"总题库：{total} 题\n"
        msg += f"✅ 已完成：{completed} 题 ({completed/total*100:.1f}%)\n"
        msg += f"🔄 进行中：{in_progress} 题\n"
        msg += f"⏭️ 已跳过：{skipped} 题\n"
        msg += f"🔥 连续打卡：{streak} 天\n"
        if completed_cats:
            msg += f"\n📂 分类完成情况：\n"
            for cat, count in completed_cats.most_common():
                msg += f"   {cat}：{count} 题\n"
        return msg

    # 查询答案
    if actions.get('query_answer'):
        if not daily_questions:
            return "⚠️ 未找到今日推送的题目记录，请先确认今日题目已推送。"
        nums = actions['query_answer']
        questions_data = load_json('data/questions.json')
        q_map = {q['id']: q for q in (questions_data if isinstance(questions_data, list) else questions_data.get('questions', []))}

        result_parts = []
        for n in nums:
            if 1 <= n <= len(daily_questions):
                q = daily_questions[n - 1]
                qid = q['id']
                full_q = q_map.get(qid, q)
                difficulty_emoji = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}
                diff = difficulty_emoji.get(full_q.get('difficulty', 'medium'), '⚪')

                part = f"{diff} 第{n}题【{full_q.get('category', '')}·{full_q.get('subcategory', '')}】\n"
                part += f"{'─' * 30}\n"
                part += f"📝 题目：\n{full_q.get('title', '')}\n\n"
                if full_q.get('leetcode_id'):
                    part += f"🔗 LeetCode {full_q['leetcode_id']}\n\n"
                answer = full_q.get('answer', full_q.get('answer_hint', '暂无详细答案'))
                part += f"💡 答案与解析：\n{answer}\n"
                result_parts.append(part)

        if result_parts:
            header = f"📖 答案解析（共{len(result_parts)}题）\n{'═' * 30}\n"
            return header + '\n'.join(result_parts)
        else:
            return "⚠️ 未找到对应题号的答案，请确认题号是否正确。"

    # 切换复习方向
    if actions.get('switch_category'):
        cat = actions['switch_category']
        progress['preferences']['preferred_categories'] = [cat]
        save_json('data/progress.json', progress)
        return f"✅ 已切换复习方向为：{cat}\n后续推送将优先该方向的题目。"

    # 设置目标公司
    if actions.get('set_target_companies'):
        companies = actions['set_target_companies']
        progress['preferences']['target_companies'] = companies
        save_json('data/progress.json', progress)
        company_names = {'bytedance': '字节跳动', 'tencent': '腾讯', 'alibaba': '阿里巴巴',
                         'meituan': '美团', 'huawei': '华为', 'xiaomi': '小米',
                         'baidu': '百度', 'unitree': '宇树科技'}
        names = [company_names.get(c, c) for c in companies]
        return f"✅ 已设置目标公司：{'、'.join(names)}\n后续推送将优先这些公司的高频题。"

    # 更新题目状态
    completed_ids = map_numbers_to_question_ids(actions.get('completed', []), daily_questions)
    skipped_ids = map_numbers_to_question_ids(actions.get('skipped', []), daily_questions)
    in_progress_ids = map_numbers_to_question_ids(actions.get('in_progress', []), daily_questions)

    if not daily_questions:
        return "⚠️ 未找到今日推送的题目记录，请先确认今日题目已推送。"

    if not completed_ids and not skipped_ids and not in_progress_ids:
        return "⚠️ 未能识别题目编号。请使用格式：\"完成1,2\" 或 \"第3题不会\""

    if completed_ids or skipped_ids:
        save_today_message_outcomes(completed_ids, skipped_ids)

    # 更新completed
    for qid in completed_ids:
        if qid not in progress['completed']:
            progress['completed'].append(qid)
        if qid in progress['in_progress']:
            progress['in_progress'].remove(qid)
        if qid in progress['skipped']:
            progress['skipped'].remove(qid)

    # 更新skipped
    for qid in skipped_ids:
        if qid not in progress['skipped']:
            progress['skipped'].append(qid)
        if qid in progress['in_progress']:
            progress['in_progress'].remove(qid)

    # 更新in_progress
    for qid in in_progress_ids:
        if qid not in progress['in_progress']:
            progress['in_progress'].append(qid)

    # 更新每日统计
    daily_stats = progress.get('daily_stats', {})
    if today not in daily_stats:
        daily_stats[today] = {'completed': 0, 'skipped': 0, 'in_progress': 0}
    daily_stats[today]['completed'] += len(completed_ids)
    daily_stats[today]['skipped'] += len(skipped_ids)
    daily_stats[today]['in_progress'] += len(in_progress_ids)
    progress['daily_stats'] = daily_stats

    # 更新连续打卡
    if completed_ids:
        last_active = progress.get('last_active_date')
        if last_active == today:
            pass  # 今天已经活跃过
        elif last_active:
            try:
                last_date = datetime.strptime(last_active, '%Y-%m-%d')
                if (get_now() - last_date).days == 1:
                    progress['streak'] = progress.get('streak', 0) + 1
                else:
                    progress['streak'] = 1
            except:
                progress['streak'] = 1
        else:
            progress['streak'] = 1
        progress['last_active_date'] = today

    # 更新total_questions
    questions_data = load_json('data/questions.json')
    progress['total_questions'] = len((questions_data if isinstance(questions_data, list) else questions_data.get('questions', [])))

    save_json('data/progress.json', progress)

    # 生成回复
    response = "📝 进度已同步\n"
    response += "━━━━━━━━━━━━━━━\n"
    if completed_ids:
        response += f"✅ 已完成：{len(completed_ids)} 题 (题号: {', '.join(str(actions['completed'][i]) for i in range(len(completed_ids)))})\n"
    if in_progress_ids:
        response += f"🔄 进行中：{len(in_progress_ids)} 题\n"
    if skipped_ids:
        response += f"⏭️ 已跳过：{len(skipped_ids)} 题\n"

    total = progress['total_questions']
    completed_count = len(progress['completed'])
    response += f"\n📊 总进度：{completed_count}/{total} ({completed_count/total*100:.1f}%)"
    response += f"\n🔥 连续打卡：{progress.get('streak', 0)} 天"

    if completed_ids and completed_count >= total:
        response += "\n\n🎉 恭喜！题库已全部完成！可以开始复习模式或扩展题库。"

    return response


def save_today_message_outcomes(completed_ids, skipped_ids):
    """Persist group-message outcomes for tomorrow's rollover."""
    log_path = os.path.join(BASE_DIR, 'data', 'daily_log.json')
    with open(log_path, 'r', encoding='utf-8-sig') as file:
        log = json.load(file)

    today_entries = [entry for entry in log if entry.get('date') == get_today_date()]
    if not today_entries:
        raise ValueError('未找到今日推送记录，无法保存题目状态')

    record_message_outcomes(today_entries[-1], completed_ids, skipped_ids)
    with open(log_path, 'w', encoding='utf-8') as file:
        json.dump(log, file, ensure_ascii=False, indent=2)


def get_answer(question_numbers, daily_questions):
    """根据题号返回今日题目的答案提示"""
    if not daily_questions:
        return "⚠️ 未找到今日推送的题目记录，请先确认今日题目已推送。"

    response_parts = []
    for n in question_numbers:
        if 1 <= n <= len(daily_questions):
            q = daily_questions[n - 1]
            answer = q.get('answer_hint', '暂无答案提示')
            response_parts.append(f"📝 第{n}题【{q.get('category', '')}·{q.get('subcategory', '')}】")
            response_parts.append(f"   {q.get('title', '')}")
            response_parts.append(f"")
            response_parts.append(f"💡 答案/思路：")
            response_parts.append(f"   {answer}")
            response_parts.append(f"{'─' * 30}")
        else:
            response_parts.append(f"⚠️ 第{n}题不存在（今日共{len(daily_questions)}题）")

    return '\n'.join(response_parts)


def process_message(message):
    """主入口：处理用户消息"""
    daily_questions = get_today_questions()
    actions = parse_progress_message(message, daily_questions)

    # 答案查询优先处理
    if actions.get('query_answer'):
        return get_answer(actions['query_answer'], daily_questions)

    if actions.get('unknown'):
        return ("🤔 未能理解你的指令。支持的格式：\n"
                "• \"完成1,2\" 或 \"1,2做完了\" → 标记完成\n"
                "• \"第3题不会\" 或 \"跳过3\" → 标记跳过\n"
                "• \"进行中2\" → 标记进行中\n"
                "• \"答案1\" 或 \"第2题答案\" → 查看解题思路\n"
                "• \"查看进度\" → 查看统计\n"
                "• \"复习算法\" → 切换复习方向\n"
                "• \"目标公司 字节,宇树\" → 设置目标公司")

    return update_progress(actions)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        user_msg = ' '.join(sys.argv[1:])
        print(process_message(user_msg))
    else:
        print("用法: python progress_sync.py \"完成1,2 第3题不会\"")
