import json, os, shutil
from collections import Counter

base = r'D:\程序\求职学习规划\interview-prep'
os.chdir(base)

parts = ['data/questions_part1.json', 'data/questions_part2.json',
         'data/questions_part3.json', 'data/questions_part4.json',
         'data/questions_part5.json', 'data/questions_part6.json']
all_questions = []
for p in parts:
    with open(p, 'r', encoding='utf-8') as f:
        d = json.load(f)
    if isinstance(d, dict):
        qs = d.get('questions', [])
        print(f'{p}: DICT format, {len(qs)} questions')
    else:
        qs = d
        print(f'{p}: LIST format, {len(qs)} questions')
    all_questions.extend(qs)

print(f'\nTotal: {len(all_questions)} questions')

ids = [q['id'] for q in all_questions]
assert len(ids) == len(set(ids)), f'Duplicate IDs! {len(ids)} vs {len(set(ids))}'
print('All IDs unique.')

no_desc = [q['id'] for q in all_questions if 'description' not in q or not q['description']]
print(f'Questions without description: {len(no_desc)}')
if no_desc:
    print('  Missing:', no_desc)

no_hint = [q['id'] for q in all_questions if 'answer_hint' not in q or not q['answer_hint']]
print(f'Questions without answer_hint: {len(no_hint)}')

cats = Counter(q['category'] for q in all_questions)
print('\nCategory distribution:')
for c, n in sorted(cats.items()):
    print(f'  {c}: {n}')

diff = Counter(q['difficulty'] for q in all_questions)
print('\nDifficulty distribution:')
for d, n in sorted(diff.items()):
    print(f'  {d}: {n}')

qtype = Counter(q['type'] for q in all_questions)
print('\nType distribution:')
for t, n in sorted(qtype.items()):
    print(f'  {t}: {n}')

# 备份原文件
shutil.copy('data/questions.json', 'data/questions.json.bak2')
print('\nBacked up original questions.json to .bak2')

# 写入新文件
with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(all_questions, f, ensure_ascii=False, indent=2)
print('Written new questions.json with full descriptions.')
