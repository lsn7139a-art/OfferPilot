import json
d = json.load(open(r'D:\程序\求职学习规划\interview-prep\data\questions_part2.json','r',encoding='utf-8'))
print(f'Count: {len(d)}')
print('IDs:')
for q in d:
    print(f'  {q["id"]} - {q["title"]}')
print()
print('Last question description length:', len(d[-1].get('description','')))
print('Last question answer_hint length:', len(d[-1].get('answer_hint','')))
print('Last question answer_hint preview:', d[-1].get('answer_hint','')[:200])
