import json, os

base = r'D:\程序\求职学习规划\interview-prep'
os.chdir(base)

with open('data/positions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 精确岗位URL映射
url_updates = {
    'unitree-ai-infra': 'https://www.unitree.com/cn/position/2046857577249112064',
    'unitree-embodied-software': 'https://www.unitree.com/position/2047604504966201344/',
    'unitree-cpp-dev': 'https://www.unitree.com/cn/position/1704702421768339456',
    'unitree-java-backend': 'https://www.unitree.com/cn/mobile/position',  # 暂未找到精确URL
    'bytedance-backend-douyin': 'https://jobs.bytedance.com/campus/m/position/detail/7665658990852852021',
    'bytedance-backend-ai-agent': 'https://jobs.bytedance.com/campus/m/position/detail/7668323746595735861',
    'netease-backend-java': 'https://campus.163.com/app/detail/index?id=3342&projectId=67',
}

updated = 0
for p in data['positions']:
    if p['id'] in url_updates:
        old_url = p['url']
        p['url'] = url_updates[p['id']]
        if old_url != p['url']:
            print(f"  {p['id']}: {old_url} -> {p['url']}")
            updated += 1

data['last_updated'] = '2026-08-23'

with open('data/positions.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\nUpdated {updated} position URLs')
