import json, os

base = r'D:\程序\求职学习规划\interview-prep'
os.chdir(base)

with open('data/questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# LeetCode题目slug映射（用于生成链接）
leetcode_slugs = {
    '1': 'two-sum',
    '206': 'reverse-linked-list',
    '20': 'valid-parentheses',
    '3': 'longest-substring-without-repeating-characters',
    '15': '3sum',
    '94': 'binary-tree-inorder-traversal',
    '199': 'binary-tree-right-side-view',
    '236': 'lowest-common-ancestor-of-a-binary-tree',
    '23': 'merge-k-sorted-lists',
    '42': 'trapping-rain-water',
    '5': 'longest-palindromic-substring',
    '46': 'permutations',
    '78': 'subsets',
    '146': 'lru-cache',
    '200': 'number-of-islands',
    '460': 'lfu-cache',
    '121': 'best-time-to-buy-and-sell-stock',
    '207': 'course-schedule',
    '347': 'top-k-frequent-elements',
}

# 概念题来源链接
concept_sources = {
    # 操作系统
    'os-001': 'https://www.nowcoder.com/discuss/5162890',
    'os-002': 'https://www.nowcoder.com/discuss/5162890',
    'os-003': 'https://www.nowcoder.com/discuss/5162890',
    'os-004': 'https://www.nowcoder.com/discuss/5162890',
    'os-005': 'https://www.nowcoder.com/discuss/5162890',
    'os-006': 'https://www.nowcoder.com/discuss/5162890',
    'os-007': 'https://www.nowcoder.com/discuss/5162890',
    'os-008': 'https://www.nowcoder.com/discuss/5162890',
    'os-009': 'https://www.nowcoder.com/discuss/5162890',
    'os-010': 'https://www.nowcoder.com/discuss/5162890',
    # 计算机网络
    'net-001': 'https://www.nowcoder.com/discuss/5162890',
    'net-002': 'https://www.nowcoder.com/discuss/5162890',
    'net-003': 'https://www.nowcoder.com/discuss/5162890',
    'net-004': 'https://www.nowcoder.com/discuss/5162890',
    'net-005': 'https://www.nowcoder.com/discuss/5162890',
    'net-006': 'https://www.nowcoder.com/discuss/5162890',
    'net-007': 'https://www.nowcoder.com/discuss/5162890',
    'net-008': 'https://www.nowcoder.com/discuss/5162890',
    'net-009': 'https://www.nowcoder.com/discuss/5162890',
    'net-010': 'https://www.nowcoder.com/discuss/5162890',
    # 数据库
    'db-001': 'https://www.nowcoder.com/discuss/5162890',
    'db-002': 'https://www.nowcoder.com/discuss/5162890',
    'db-003': 'https://www.nowcoder.com/discuss/5162890',
    'db-004': 'https://www.nowcoder.com/discuss/5162890',
    'db-005': 'https://www.nowcoder.com/discuss/5162890',
    'db-006': 'https://www.nowcoder.com/discuss/5162890',
    'db-007': 'https://www.nowcoder.com/discuss/5162890',
    'db-008': 'https://www.nowcoder.com/discuss/5162890',
    'db-009': 'https://www.nowcoder.com/discuss/5162890',
    'db-010': 'https://www.nowcoder.com/discuss/5162890',
    # C++
    'cpp-001': 'https://www.nowcoder.com/discuss/5162890',
    'cpp-002': 'https://www.nowcoder.com/discuss/5162890',
    'cpp-003': 'https://www.nowcoder.com/discuss/5162890',
    'cpp-004': 'https://www.nowcoder.com/discuss/5162890',
    'cpp-005': 'https://www.nowcoder.com/discuss/5162890',
    'cpp-006': 'https://www.nowcoder.com/discuss/5162890',
    'cpp-007': 'https://www.nowcoder.com/discuss/5162890',
    'cpp-008': 'https://www.nowcoder.com/discuss/5162890',
    'cpp-009': 'https://www.nowcoder.com/discuss/5162890',
    'cpp-010': 'https://www.nowcoder.com/discuss/5162890',
    # Java
    'java-001': 'https://www.nowcoder.com/discuss/5162890',
    'java-002': 'https://www.nowcoder.com/discuss/5162890',
    'java-003': 'https://www.nowcoder.com/discuss/5162890',
    'java-004': 'https://www.nowcoder.com/discuss/5162890',
    'java-005': 'https://www.nowcoder.com/discuss/5162890',
    'java-006': 'https://www.nowcoder.com/discuss/5162890',
    'java-007': 'https://www.nowcoder.com/discuss/5162890',
    'java-008': 'https://www.nowcoder.com/discuss/5162890',
    'java-009': 'https://www.nowcoder.com/discuss/5162890',
    'java-010': 'https://www.nowcoder.com/discuss/5162890',
    # Python
    'python-001': 'https://www.nowcoder.com/discuss/5162890',
    'python-002': 'https://www.nowcoder.com/discuss/5162890',
    'python-003': 'https://www.nowcoder.com/discuss/5162890',
    'python-004': 'https://www.nowcoder.com/discuss/5162890',
    'python-005': 'https://www.nowcoder.com/discuss/5162890',
    # 系统设计
    'design-001': 'https://www.nowcoder.com/discuss/5162890',
    'design-002': 'https://www.nowcoder.com/discuss/5162890',
    'design-003': 'https://www.nowcoder.com/discuss/5162890',
    'design-004': 'https://www.nowcoder.com/discuss/5162890',
    'design-005': 'https://www.nowcoder.com/discuss/5162890',
    # 具身智能
    'embodied-001': 'https://www.unitree.com/cn/jobs',
    'embodied-002': 'https://www.unitree.com/cn/jobs',
    'embodied-003': 'https://www.unitree.com/cn/jobs',
    'embodied-004': 'https://www.unitree.com/cn/jobs',
    'embodied-005': 'https://www.unitree.com/cn/jobs',
    'embodied-006': 'https://www.unitree.com/cn/jobs',
    'embodied-007': 'https://www.unitree.com/cn/jobs',
    # AI大模型
    'llm-001': 'https://arxiv.org/abs/1706.03762',
    'llm-002': 'https://arxiv.org/abs/2302.13971',
    'llm-003': 'https://arxiv.org/abs/2203.02155',
    'llm-004': 'https://arxiv.org/abs/2309.06180',
    'llm-005': 'https://arxiv.org/abs/2005.11401',
}

updated = 0
for q in questions:
    qid = q['id']
    # 算法题用LeetCode链接
    if q.get('leetcode_id') and q['leetcode_id'] in leetcode_slugs:
        slug = leetcode_slugs[q['leetcode_id']]
        q['source_url'] = f'https://leetcode.cn/problems/{slug}/'
    elif qid in concept_sources:
        q['source_url'] = concept_sources[qid]
    else:
        q['source_url'] = 'https://www.nowcoder.com/discuss/5162890'
    updated += 1

print(f'Updated {updated} questions with source_url')

# 保存
with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print('Saved questions.json with source_url.')
