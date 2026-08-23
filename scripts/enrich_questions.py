import json, os

base = r'D:\程序\求职学习规划\interview-prep'
os.chdir(base)

with open('data/questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

# 按分类设定默认出处和面向岗位
category_defaults = {
    '算法': {
        'source': 'LeetCode Hot 100 / CodeTop大厂高频',
        'target_roles': ['后端开发', 'C++开发', '算法工程师', '测试开发', '全栈']
    },
    '操作系统': {
        'source': '字节跳动/腾讯后端面试真题 · 《小林coding系统拆解》',
        'target_roles': ['后端开发', 'C++开发', '基础设施', '嵌入式']
    },
    '计算机网络': {
        'source': '腾讯/字节跳动后端面试真题 · 《图解HTTP》',
        'target_roles': ['后端开发', '全栈', '测试开发', '网络工程师']
    },
    '数据库': {
        'source': '阿里/美团后端面试真题 · 《MySQL实战45讲》',
        'target_roles': ['后端开发', '全栈', 'DBA', '数据开发']
    },
    'C++': {
        'source': '腾讯/字节跳动C++面试真题 · 《深度探索C++对象模型》',
        'target_roles': ['C++开发', '客户端开发', '游戏开发', '机器人软件', '基础设施']
    },
    'Java': {
        'source': '阿里/美团Java后端面试真题 · 《Java并发编程实战》',
        'target_roles': ['Java后端', '全栈', '大数据开发', '中间件开发']
    },
    'Python': {
        'source': '字节跳动/美团Python面试真题 · 《流畅的Python》',
        'target_roles': ['Python后端', '算法工程师', '数据开发', 'AI应用开发']
    },
    '系统设计': {
        'source': '字节跳动/美团高级后端面试 · 《设计数据密集型应用》',
        'target_roles': ['后端高级', '架构师', '全栈', '技术专家']
    },
    '具身智能': {
        'source': '宇树科技/人形机器人算法岗面试真题 · 具身智能大模型',
        'target_roles': ['机器人软件工程师', '具身智能算法', '运动控制算法', '感知算法']
    },
    'AI大模型': {
        'source': '字节跳动/百度大模型面试真题 · 大模型应用开发',
        'target_roles': ['大模型算法', 'AI应用开发', 'NLP算法', '推荐算法']
    }
}

# 个别题目特殊调整
special_overrides = {
    # 算法题中偏特定方向的
    'algo-015': {'source': 'LeetCode 200 · 亚马逊/微软面试高频'},
    'algo-016': {'source': 'LeetCode 460 · 字节跳动后端面试真题'},
    'algo-018': {'source': 'LeetCode 207/210 · 美团/阿里面试真题'},
    # 具身智能特殊
    'embodied-001': {'source': '宇树科技具身智能软件工程师面试真题'},
    'embodied-002': {'source': '宇树科技运动控制算法岗面试真题 · Isaac Gym'},
    'embodied-005': {'source': '机器人软件工程师面试真题 · ROS2官方文档'},
    # AI大模型特殊
    'llm-001': {'source': '大模型算法岗面试真题 · 《Attention Is All You Need》'},
    'llm-002': {'source': '大模型预训练算法岗面试真题 · LLaMA技术报告'},
    'llm-003': {'source': '大模型对齐算法岗面试真题 · InstructGPT论文'},
    'llm-004': {'source': '大模型推理优化岗面试真题 · vLLM/FlashAttention'},
    'llm-005': {'source': '大模型应用开发面试真题 · LangChain/AutoGen'},
    # 系统设计特殊
    'design-001': {'source': '字节跳动后端二面系统设计真题'},
    'design-002': {'source': '阿里/美团秒杀系统设计真题'},
    'design-003': {'source': '字节跳动中间件面试真题 · Kafka/RocketMQ'},
    'design-005': {'source': '字节跳动基础设施面试真题 · Dubbo/gRPC'},
}

updated = 0
for q in questions:
    cat = q.get('category', '')
    defaults = category_defaults.get(cat, {
        'source': '大厂面试高频题',
        'target_roles': ['后端开发']
    })

    # 应用默认值
    if 'source' not in q or not q['source']:
        q['source'] = defaults.get('source', '大厂面试高频题')
    if 'target_roles' not in q or not q['target_roles']:
        q['target_roles'] = defaults.get('target_roles', ['后端开发'])

    # 应用特殊覆盖
    if q['id'] in special_overrides:
        override = special_overrides[q['id']]
        if 'source' in override:
            q['source'] = override['source']
        if 'target_roles' in override:
            q['target_roles'] = override['target_roles']

    updated += 1

print(f'Updated {updated} questions')

# 验证
no_source = [q['id'] for q in questions if not q.get('source')]
no_roles = [q['id'] for q in questions if not q.get('target_roles')]
print(f'Without source: {len(no_source)}')
print(f'Without target_roles: {len(no_roles)}')

# 统计面向岗位
from collections import Counter
all_roles = Counter()
for q in questions:
    for r in q.get('target_roles', []):
        all_roles[r] += 1
print('\n面向岗位分布:')
for r, n in all_roles.most_common():
    print(f'  {r}: {n}题')

# 保存
with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)
print('\nSaved questions.json with source and target_roles.')
