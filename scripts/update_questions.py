#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库更新脚本
- 检查题库完整性
- 支持手动添加新题目
- 统计题库分布
- 预留爬虫接口（可扩展为自动爬取牛客/面经网站）
"""

import json
import os
from collections import Counter
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_json(filepath):
    full_path = os.path.join(BASE_DIR, filepath)
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    full_path = os.path.join(BASE_DIR, filepath)
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def show_stats():
    """显示题库统计"""
    data = load_json('data/questions.json')
    questions = data.get('questions', [])

    print(f"📚 题库统计 (共 {len(questions)} 题)")
    print("=" * 40)

    # 按分类
    cat_counter = Counter(q.get('category', '未知') for q in questions)
    print("\n📂 按分类：")
    for cat, count in cat_counter.most_common():
        print(f"   {cat}：{count} 题")

    # 按难度
    diff_counter = Counter(q.get('difficulty', '未知') for q in questions)
    print("\n📊 按难度：")
    for diff, count in diff_counter.most_common():
        emoji = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}.get(diff, '⚪')
        print(f"   {emoji} {diff}：{count} 题")

    # 按题型
    type_counter = Counter(q.get('type', '未知') for q in questions)
    print("\n📝 按题型：")
    for t, count in type_counter.most_common():
        print(f"   {t}：{count} 题")

    # 按公司
    company_counter = Counter()
    for q in questions:
        for c in q.get('companies', []):
            company_counter[c] += 1
    print("\n🏢 按公司出现频次：")
    company_names = {
        'bytedance': '字节跳动', 'tencent': '腾讯', 'alibaba': '阿里巴巴',
        'meituan': '美团', 'huawei': '华为', 'xiaomi': '小米',
        'baidu': '百度', 'unitree': '宇树科技', 'jd': '京东',
        'netease': '网易', 'sohu': '搜狐'
    }
    for cid, count in company_counter.most_common():
        print(f"   {company_names.get(cid, cid)}：{count} 题")

    # 检查数据完整性
    print("\n🔍 数据完整性检查：")
    issues = []
    for q in questions:
        if not q.get('id'):
            issues.append(f"缺少id: {q.get('title', '未知')[:30]}")
        if not q.get('title'):
            issues.append(f"缺少title: {q.get('id')}")
        if not q.get('category'):
            issues.append(f"缺少category: {q.get('id')}")
        if not q.get('difficulty'):
            issues.append(f"缺少difficulty: {q.get('id')}")
        if not q.get('answer_hint'):
            issues.append(f"缺少answer_hint: {q.get('id')}")

    if issues:
        print(f"   ⚠️ 发现 {len(issues)} 个问题：")
        for issue in issues[:10]:
            print(f"      - {issue}")
    else:
        print("   ✅ 所有题目数据完整")

    return data


def add_question(question_data):
    """手动添加一道题目"""
    data = load_json('data/questions.json')
    questions = data.get('questions', [])

    # 自动生成id
    existing_ids = set(q['id'] for q in questions)
    new_id = question_data.get('id')
    if not new_id:
        cat_prefix = question_data.get('category', 'q')[:2].lower()
        i = 1
        while f"{cat_prefix}-{i:03d}" in existing_ids:
            i += 1
        new_id = f"{cat_prefix}-{i:03d}"
        question_data['id'] = new_id

    if new_id in existing_ids:
        print(f"⚠️ 题目ID {new_id} 已存在，跳过")
        return None

    questions.append(question_data)
    data['questions'] = questions
    data['total_questions'] = len(questions)
    data['last_updated'] = datetime.now().strftime('%Y-%m-%d')

    save_json('data/questions.json', data)
    print(f"✅ 已添加题目：{new_id} - {question_data.get('title', '')[:50]}")
    return new_id


def batch_add_from_web(company=None, category=None):
    """
    预留：从网络爬取新题目
    实际使用时可接入牛客网、GitHub面经仓库等数据源
    """
    print("🌐 题库自动更新（预留接口）")
    print("=" * 40)
    print("当前版本支持手动添加题目。")
    print("自动爬取功能可扩展接入：")
    print("  - 牛客网面经 (nowcoder.com)")
    print("  - GitHub校招面试题仓库")
    print("  - 各公司官网招聘页面")
    print("  - 技术博客面经汇总")
    print("\n建议每周手动更新一次，或扩展爬虫脚本实现自动化。")


def main():
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'stats':
            show_stats()
        elif cmd == 'update':
            batch_add_from_web()
        else:
            print("用法: python update_questions.py [stats|update]")
    else:
        show_stats()


if __name__ == '__main__':
    main()
