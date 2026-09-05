#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日面试题推送脚本（岗位+题目版）
- 每天推送1个具体岗位（含公司/地点/薪资/链接/详细要求）
- 根据岗位方向智能匹配3-4道题目
- 生成格式化的每日推送消息
- 记录推送日志
"""

import json
import random
import os
from datetime import datetime, timedelta
from collections import Counter
from time_utils import get_today_date, get_weekday_cn, get_isoformat, set_timezone

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


def select_position(positions, progress):
    """
    选择今日岗位：
    - 轮询机制，避免重复
    - 优先选择目标公司的岗位
    """
    target_companies = set(progress.get('preferences', {}).get('target_companies', []))
    recent_positions = progress.get('recent_positions', [])

    # 排除最近7天推过的岗位
    available = [p for p in positions if p['id'] not in set(recent_positions[-7:])]
    if not available:
        available = positions  # 全部推过了，重置

    # 目标公司岗位优先
    target_positions = [p for p in available if p['company_id'] in target_companies]
    if target_positions and random.random() < 0.6:
        return random.choice(target_positions)

    return random.choice(available)


def select_questions(questions, progress, config, position, count=3):
    """
    智能选题策略（基于岗位方向）：
    1. 优先选择岗位匹配方向的题目
    2. 优先复习即将到期的题目
    3. 薄弱领域加权
    4. 目标公司高频题优先
    5. 已完成/跳过的题目排除
    """
    completed_ids = set(progress.get('completed', []))
    skipped_ids = set(progress.get('skipped', []))
    in_progress_ids = set(progress.get('in_progress', []))

    # 排除已完成和跳过的
    available = [q for q in questions
                 if q['id'] not in completed_ids
                 and q['id'] not in skipped_ids]

    if not available:
        available = [q for q in questions if q['id'] in completed_ids]
        if not available:
            return []

    # 岗位匹配方向
    match_categories = set(position.get('match_categories', []))
    match_tags = set(position.get('match_tags', []))
    target_companies = set(progress.get('preferences', {}).get('target_companies', []))
    weak_areas = set(progress.get('weak_areas', []))
    difficulty_weight = progress.get('preferences', {}).get('difficulty_weight',
                                                              {'easy': 0.3, 'medium': 0.5, 'hard': 0.2})

    scored = []
    for q in available:
        score = 0.0
        # 岗位匹配方向加分（最重要）
        if q.get('category') in match_categories:
            score += 8
        if any(tag in match_tags for tag in q.get('tags', [])):
            score += 4
        # 岗位匹配公司加分
        if position['company_id'] in q.get('companies', []):
            score += 5
        # 目标公司加分
        if target_companies and any(c in target_companies for c in q.get('companies', [])):
            score += 2
        # 薄弱领域加分
        if q.get('category') in weak_areas or q.get('subcategory') in weak_areas:
            score += 3
        # 进行中的题优先
        if q['id'] in in_progress_ids:
            score += 6
        # 难度权重
        score += difficulty_weight.get(q.get('difficulty', 'medium'), 0.3) * 2
        # 随机扰动
        score += random.uniform(0, 1)
        scored.append((score, q))

    # 按分数排序，取前 count*2 后随机选 count（增加多样性）
    scored.sort(key=lambda x: x[0], reverse=True)
    top_candidates = scored[:max(count * 3, count)]
    selected = random.sample([q for _, q in top_candidates], min(count, len(top_candidates)))

    return selected


def format_position_section(position):
    """格式化岗位详情部分"""
    lines = []
    lines.append(f"💼 今日岗位：{position['company_name']}・{position['title']}")
    lines.append("")
    lines.append(f"📍 地点：{position['location']}")
    lines.append(f"💰 薪资：{position.get('salary', '面议')}")
    lines.append(f"🏢 部门：{position.get('department', '')}")
    lines.append(f"🔗 岗位链接：{position['url']}")
    lines.append("")

    # 核心要求（取前5条）
    requirements = position.get('requirements', [])[:5]
    if requirements:
        lines.append("📋 核心要求：")
        for i, req in enumerate(requirements, 1):
            # 截断过长的要求
            if len(req) > 60:
                req = req[:57] + "..."
            lines.append(f"   {i}. {req}")

    return lines


def format_daily_message(position, selected_questions, progress, companies_data):
    """格式化为飞书推送消息（岗位+题目版）"""
    today = get_today_date()
    weekday = get_weekday_cn()

    # 统计进度
    total = progress.get('total_questions', 0)
    completed_count = len(progress.get('completed', []))
    streak = progress.get('streak', 0)

    lines = []
    lines.append(f"{today} {weekday}・每日面试题打卡")
    lines.append(f"📊 进度：{completed_count}/{total} 题 | 连续打卡 {streak} 天")
    lines.append("─" * 30)

    # 岗位详情部分
    lines.extend(format_position_section(position))
    lines.append("")
    lines.append("─" * 30)

    # 题目部分
    company_map = {c['id']: c['name'] for c in companies_data.get('companies', [])}

    for i, q in enumerate(selected_questions, 1):
        difficulty_emoji = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}
        diff = difficulty_emoji.get(q.get('difficulty', 'medium'), '⚪')

        company_names = [company_map.get(c, c) for c in q.get('companies', [])[:3]]
        company_str = '、'.join(company_names) if company_names else '通用'

        lines.append(f"\n{diff} 第 {i} 题【{q.get('category', '')}・{q.get('subcategory', '')}】")
        lines.append("")
        lines.append(f"出现于：{company_str}")
        if q.get('leetcode_id'):
            lines.append(f"🔗 LeetCode {q['leetcode_id']}")
        # 题目来源链接
        source_url = q.get('source_url', '')
        if source_url:
            lines.append(f"📎 来源：{source_url}")
        lines.append("")
        # 极简格式：只显示一句话题目
        lines.append(q.get('title', ''))

    lines.append("\n" + "─" * 30)
    lines.append("💡 回复指令：")
    lines.append("   「答案1」→ 查看第1题解析")
    lines.append("   「完成1,2 第3题不会」→ 标记进度")
    lines.append("   「跳过3」→ 跳过某题")
    lines.append("   「查看进度」→ 查看统计")
    lines.append("   「岗位详情」→ 查看今日岗位完整要求")

    return '\n'.join(lines)


def log_daily_push(position, selected_questions):
    """记录每日推送日志"""
    log_path = os.path.join(BASE_DIR, 'data', 'daily_log.json')
    if os.path.exists(log_path):
        with open(log_path, 'r', encoding='utf-8-sig') as f:
            log = json.load(f)
    else:
        log = []

    today = get_today_date()
    entry = {
        'date': today,
        'timestamp': get_isoformat(),
        'position_id': position['id'],
        'position_title': f"{position['company_name']}・{position['title']}",
        'question_ids': [q['id'] for q in selected_questions],
        'question_titles': [q['title'][:50] for q in selected_questions],
        'task_guids': []  # 待飞书任务创建后回填
    }
    log.append(entry)

    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    # 更新progress中的recent_positions
    progress_path = os.path.join(BASE_DIR, 'data', 'progress.json')
    with open(progress_path, 'r', encoding='utf-8-sig') as f:
        progress = json.load(f)
    if 'recent_positions' not in progress:
        progress['recent_positions'] = []
    progress['recent_positions'].append(position['id'])
    # 只保留最近30天
    if len(progress['recent_positions']) > 30:
        progress['recent_positions'] = progress['recent_positions'][-30:]
    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def main():
    config = load_json('config.json')
    questions_data = load_json('data/questions.json')
    # 兼容 list 和 dict 两种格式
    if isinstance(questions_data, list):
        questions = questions_data
    else:
        questions = questions_data.get('questions', [])
    progress = load_json('data/progress.json')
    companies_data = load_json('data/companies.json')
    positions_data = load_json('data/positions.json')
    positions = positions_data.get('positions', [])

    daily_count = config.get('question_selection', {}).get('daily_count', 3)

    if not positions:
        print("⚠️ 岗位库为空，请检查positions.json")
        return

    # 选岗位
    position = select_position(positions, progress)
    print(f"今日岗位：{position['company_name']}・{position['title']}")

    # 选题（基于岗位方向）
    selected = select_questions(questions, progress, config, position, daily_count)

    if not selected:
        print("⚠️ 题库中没有可选题目，请检查题库数据。")
        return

    # 生成消息
    message = format_daily_message(position, selected, progress, companies_data)

    # 记录日志
    log_daily_push(position, selected)

    # 输出消息（供飞书推送使用）
    print(message)

    # 同时保存到文件
    output_path = os.path.join(BASE_DIR, 'data', 'last_daily_message.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(message)

    print(f"\n✅ 已生成 {len(selected)} 道题目（匹配岗位：{position['title']}），消息已保存到 {output_path}")


if __name__ == '__main__':
    main()
