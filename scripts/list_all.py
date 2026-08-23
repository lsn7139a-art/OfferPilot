import json

with open(r'D:\程序\求职学习规划\interview-prep\data\questions.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

print(f'Total: {len(qs)}')
print(f'Fields: {list(qs[0].keys())}')
print()
for q in qs:
    companies = '、'.join(q.get('companies', [])[:3])
    roles = '、'.join(q.get('target_roles', [])[:3])
    print(f'{q["id"]:12} | {q["category"]:6} | {q["difficulty"]:6} | {q["type"]:7} | {companies:20} | {roles:20} | {q["title"][:45]}')
