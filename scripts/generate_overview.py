import json, os
from collections import defaultdict

base = r'D:\程序\求职学习规划\interview-prep'
os.chdir(base)

with open('data/questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

with open('data/companies.json', 'r', encoding='utf-8') as f:
    companies_data = json.load(f)

company_map = {c['id']: c['name'] for c in companies_data.get('companies', [])}

# 按分类分组
by_category = defaultdict(list)
for q in questions:
    by_category[q['category']].append(q)

lines = []
lines.append('# 面试题库总览')
lines.append('')
lines.append(f'**题目总数：{len(questions)} 道**')
lines.append('')
lines.append('## 分类统计')
lines.append('')
lines.append('| 分类 | 题数 | 简单 | 中等 | 困难 |')
lines.append('|------|------|------|------|------|')
for cat in sorted(by_category.keys()):
    qs = by_category[cat]
    easy = sum(1 for q in qs if q['difficulty'] == 'easy')
    medium = sum(1 for q in qs if q['difficulty'] == 'medium')
    hard = sum(1 for q in qs if q['difficulty'] == 'hard')
    lines.append(f'| {cat} | {len(qs)} | {easy} | {medium} | {hard} |')

lines.append('')
lines.append('---')
lines.append('')

# 每题详情
for cat in sorted(by_category.keys()):
    qs = by_category[cat]
    lines.append(f'## {cat}（{len(qs)}道）')
    lines.append('')
    for q in qs:
        diff_emoji = {'easy': '🟢', 'medium': '🟡', 'hard': '🔴'}[q['difficulty']]
        type_label = {'coding': '代码题', 'concept': '概念题', 'design': '设计题'}[q['type']]
        companies = '、'.join(company_map.get(c, c) for c in q.get('companies', [])[:3])
        roles = '、'.join(q.get('target_roles', [])[:3])
        lines.append(f'### {diff_emoji} {q["id"]}｜{type_label}｜{q["subcategory"]}')
        lines.append('')
        lines.append(f'**题目：** {q["title"]}')
        lines.append('')
        lines.append(f'**出现公司：** {companies}')
        lines.append(f'**面向岗位：** {roles}')
        lines.append(f'**来源链接：** {q.get("source_url", "无")}')
        if q.get('leetcode_id'):
            lines.append(f'**LeetCode：** {q["leetcode_id"]}')
        lines.append('')

# 保存
output_path = os.path.join(base, '题库总览.md')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'Generated {output_path}')
print(f'Total questions: {len(questions)}')
