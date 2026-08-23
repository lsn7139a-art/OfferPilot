import json
from collections import Counter

base = r'D:\程序\求职学习规划\interview-prep'

with open(f'{base}/data/companies.json', 'r', encoding='utf-8') as f:
    c = json.load(f)

print('=== companies.json（8家公司详细JD）===')
for x in c.get('companies', []):
    print(f'{x["id"]:12} | {x["name"]}')

print()
with open(f'{base}/data/questions.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

cnt = Counter()
for q in qs:
    cnt.update(q.get('companies', []))

print('=== 题目出现公司分布 ===')
for k, v in cnt.most_common():
    print(f'{k:12} | {v}题')
