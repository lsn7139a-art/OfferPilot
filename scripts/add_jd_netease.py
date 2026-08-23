import json, os

base = r'D:\程序\求职学习规划\interview-prep'
os.chdir(base)

with open('data/companies.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 检查是否已存在
existing_ids = {c['id'] for c in data['companies']}
print(f'Existing companies: {existing_ids}')

# 京东
jd_company = {
    "id": "jd",
    "name": "京东",
    "aliases": ["JD", "京东集团", "京东零售"],
    "locations": ["北京", "上海", "深圳", "成都", "武汉", "南京"],
    "positions": [
        {
            "title": "后端开发工程师",
            "level": "校招/实习",
            "requirements": [
                "计算机相关专业，本科及以上学历",
                "熟练掌握C/C++/Java/Go至少一种编程语言",
                "扎实的数据结构与算法基础，LeetCode中等难度水平",
                "熟悉TCP/IP、HTTP、HTTPS等网络协议",
                "熟悉MySQL/Oracle等关系型数据库及SQL优化",
                "熟悉Redis、Memcached、MongoDB等NoSQL解决方案",
                "了解分布式系统原理，熟悉多线程、消息队列(Kafka/RabbitMQ)",
                "Java方向需熟悉Spring、Spring Boot、MyBatis等框架",
                "有大数据生态(ClickHouse/Hadoop/Spark/Flink)经验者优先",
                "算法题必考：CodeTop京东高频 + LeetCode Hot 100"
            ],
            "interview_rounds": "笔试(算法+选择题) → 一面(基础+算法) → 二面(项目+系统设计+算法) → 三面(综合) → HR面",
            "focus_areas": ["算法", "Java基础", "操作系统", "计算机网络", "数据库", "分布式系统"]
        },
        {
            "title": "C++开发工程师",
            "level": "校招/实习",
            "requirements": [
                "精通C++编程语言，熟悉STL、智能指针、多线程",
                "熟悉Linux系统编程，了解网络编程(socket/epoll)",
                "扎实的数据结构与算法基础",
                "熟悉MySQL、Redis等存储组件",
                "有高性能服务开发经验者优先"
            ],
            "interview_rounds": "笔试 → 一面(C++基础+算法) → 二面(项目+系统设计) → 三面 → HR面",
            "focus_areas": ["算法", "C++", "操作系统", "计算机网络", "数据库"]
        }
    ],
    "culture": "客户为先、创新、拼搏、担当、感恩、诚信",
    "source_url": "https://campus.jd.com/"
}

# 网易
netease_company = {
    "id": "netease",
    "name": "网易",
    "aliases": ["NetEase", "网易互娱", "网易雷火", "网易云音乐"],
    "locations": ["杭州", "广州", "北京", "上海", "深圳"],
    "positions": [
        {
            "title": "后端开发工程师",
            "level": "校招/实习",
            "requirements": [
                "本科及以上学历，计算机相关专业",
                "扎实的Java编程基础，熟悉JVM原理和性能优化",
                "熟悉Spring Framework、Spring Boot、Spring Cloud等全家桶",
                "熟练使用Unix/Linux操作系统，熟悉RESTful API、Servlet、Tomcat",
                "熟悉MySQL、Redis等数据库的使用和优化",
                "了解Kafka等消息队列",
                "有分布式系统设计与调优能力者优先",
                "对AI应用(ChatGPT/智能助手/AI搜索)有兴趣者优先",
                "算法题必考：LeetCode Hot 100 + 网易高频"
            ],
            "interview_rounds": "笔试(算法) → 一面(基础+算法手撕) → 二面(系统设计+专业深挖) → 三面(综合) → HR面",
            "focus_areas": ["算法", "Java基础", "JVM", "计算机网络", "数据库", "系统设计"]
        },
        {
            "title": "游戏研发工程师(C++)",
            "level": "校招/实习",
            "requirements": [
                "精通C++编程语言，熟悉C++11/14/17新特性",
                "熟悉数据结构与算法，有扎实的编程基础",
                "了解计算机图形学基础(渲染管线、Shader、OpenGL/D3D)",
                "熟悉游戏引擎(Unity/Unreal)者优先",
                "有游戏项目开发经验者优先"
            ],
            "interview_rounds": "笔试(算法+C++基础) → 一面(C+++算法) → 二面(图形学/游戏引擎+项目) → 三面 → HR面",
            "focus_areas": ["算法", "C++", "计算机图形学", "数据结构", "操作系统"]
        }
    ],
    "culture": "网易文化：热爱、创新、协作、担当",
    "source_url": "https://campus.163.com/"
}

# 添加
if 'jd' not in existing_ids:
    data['companies'].append(jd_company)
    print('Added 京东')
else:
    print('京东 already exists, skipping')

if 'netease' not in existing_ids:
    data['companies'].append(netease_company)
    print('Added 网易')
else:
    print('网易 already exists, skipping')

data['last_updated'] = '2026-08-23'

# 保存
with open('data/companies.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\nTotal companies now: {len(data["companies"])}')
print('Companies:', [c['name'] for c in data['companies']])
