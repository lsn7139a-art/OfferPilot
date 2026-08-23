import json, os

base = r'D:\程序\求职学习规划\interview-prep'
os.chdir(base)

positions = {
    "last_updated": "2026-08-23",
    "positions": [
        # ========== 宇树科技 ==========
        {
            "id": "unitree-ai-infra",
            "company_id": "unitree",
            "company_name": "宇树科技",
            "title": "AI Infra工程师",
            "location": "杭州市",
            "salary": "20-50K",
            "job_type": "技术类",
            "department": "研发部",
            "url": "https://www.unitree.com/cn/position/2046857577249112064",
            "responsibilities": [
                "负责大规模算力集群下AI框架的设计与建设",
                "构建并维护大规模算力集群的分布式训练系统，支持大模型训练",
                "优化大模型训练GPU利用率、内存占用和训练吞吐量，消除训练瓶颈",
                "优化数据加载器效率，缩短从数据到达模型训练的耗时",
                "构建低延迟推理流水线：用于机器人实时控制，应用量化、蒸馏和模型编译等技术"
            ],
            "requirements": [
                "具备千卡级GPU集群训练实践，熟悉大模型训练中的常见问题与系统级解决方案",
                "熟练掌握DDP/FSDP等分布式机制底层原理",
                "熟练运用DeepSpeed、Megatron-LM等主流框架",
                "具备全栈性能分析能力，能高效识别计算、通信与数据加载链路中的关键瓶颈",
                "有ML Infra或AI训练平台构建经验者优先",
                "有多模态大模型及强化学习训练经验者优先"
            ],
            "match_categories": ["AI大模型", "操作系统", "算法"],
            "match_tags": ["分布式训练", "DeepSpeed", "GPU", "推理优化", "大模型"]
        },
        {
            "id": "unitree-embodied-software",
            "company_id": "unitree",
            "company_name": "宇树科技",
            "title": "具身智能软件工程师",
            "location": "杭州市",
            "salary": "20-50K",
            "job_type": "技术类",
            "department": "研发部",
            "url": "https://www.unitree.com/cn/mobile/position",
            "responsibilities": [
                "负责具身智能算法和模型在机器人上的开发与集成，转化为稳定的产品功能",
                "负责模型在嵌入式硬件（Jetson Orin/Thor, 昇腾等）上的优化与部署",
                "优化机器人软件架构，降低系统延迟，确保感知-决策-执行链路的高频稳定响应",
                "构建具身智能数据采集、存储、清洗、标注等软件系统和平台",
                "设计完善的异常处理机制，确保机器人在算法失效、传感器异常等突发状况下安全停机或自我恢复"
            ],
            "requirements": [
                "扎实的C++/Python编程基础，熟悉Linux系统编程",
                "熟悉模型部署与优化技术（量化、剪枝、蒸馏、TensorRT/ONNX等）",
                "了解机器人软件架构（ROS/自研中间件），有嵌入式开发经验者优先",
                "有具身智能/机器人项目经验者优先",
                "熟悉多模态大模型应用开发者优先"
            ],
            "match_categories": ["具身智能", "C++", "Python", "操作系统"],
            "match_tags": ["模型部署", "嵌入式", "ROS", "C++", "Python"]
        },
        {
            "id": "unitree-cpp-dev",
            "company_id": "unitree",
            "company_name": "宇树科技",
            "title": "C++开发工程师(J10034)",
            "location": "杭州市",
            "salary": "20-40K",
            "job_type": "技术类",
            "department": "研发部",
            "url": "https://www.unitree.com/cn/mobile/position",
            "responsibilities": [
                "负责公司软件架构的升级、优化",
                "负责公司API的集成、测试，并持续优化",
                "负责产品软件的升级、降级、系统修复",
                "与产品团队配合，完成B端大客户的定制化需求"
            ],
            "requirements": [
                "精通C++编程语言，熟悉C++11/14/17新特性",
                "熟悉数据结构与算法，有扎实的编程基础",
                "熟悉Linux系统编程，了解网络编程(socket/epoll)",
                "有软件架构设计经验者优先",
                "有机器人/嵌入式相关项目经验者优先"
            ],
            "match_categories": ["C++", "操作系统", "计算机网络", "算法"],
            "match_tags": ["C++", "Linux", "网络编程", "软件架构"]
        },
        {
            "id": "unitree-java-backend",
            "company_id": "unitree",
            "company_name": "宇树科技",
            "title": "JAVA后端开发工程师(J10096)",
            "location": "杭州市",
            "salary": "15-30K",
            "job_type": "技术类",
            "department": "研发部",
            "url": "https://www.unitree.com/cn/mobile/position",
            "responsibilities": [
                "负责移动端产品的后台服务端搭建与编写API开发文档",
                "持续优化服务端的性能、稳定性、效率和服务器成本",
                "公司数据存储部分安全性维护"
            ],
            "requirements": [
                "精通Java编程语言，熟悉JVM原理",
                "熟悉Spring Boot/Spring Cloud等框架",
                "熟悉MySQL、Redis等存储组件",
                "有高并发服务开发经验者优先",
                "熟悉Linux系统和网络协议"
            ],
            "match_categories": ["Java", "数据库", "计算机网络", "操作系统"],
            "match_tags": ["Java", "Spring", "MySQL", "Redis"]
        },
        # ========== 字节跳动 ==========
        {
            "id": "bytedance-backend-douyin",
            "company_id": "bytedance",
            "company_name": "字节跳动",
            "title": "后端工程师 - 抖音平台产品",
            "location": "北京、成都",
            "salary": "25-50K",
            "job_type": "研发-后端",
            "department": "抖音平台产品",
            "url": "https://jobs.bytedance.com/campus/m/position/detail/7665658990852852021",
            "responsibilities": [
                "负责前端和服务端的业务开发工作，覆盖业务全链路",
                "深度运用AI Coding工具，开发并维护基于MCP、CLI、Skills等的各类工具",
                "参与AI研发基础设施与Agent工作流建设",
                "推动Vibe coding、Spec Coding等新型AI研发范式落地",
                "负责前沿技术探索与范式推广，跟进AI/LLM最新进展"
            ],
            "requirements": [
                "2027届本科及以上学历，计算机、通信、电子信息、数学等相关专业",
                "具备良好的计算机基础（数据结构、算法、计算机网络、操作系统）",
                "熟练使用至少一门编程语言",
                "熟练使用HTML5/CSS3/JS/TS/Vue/React等前端技术，有全栈(Golang)开发经验者优先",
                "熟练使用TRAE/Claude Code/Codex/Cursor等AI Coding工具者优先",
                "认可AI Coder定位，具备较强学习能力和适应能力"
            ],
            "match_categories": ["算法", "操作系统", "计算机网络", "数据库", "Java"],
            "match_tags": ["后端", "全栈", "Golang", "AI Coding", "分布式"]
        },
        {
            "id": "bytedance-backend-ai-agent",
            "company_id": "bytedance",
            "company_name": "字节跳动",
            "title": "后端研发工程师(AI Agent方向)",
            "location": "北京",
            "salary": "30-60K",
            "job_type": "研发-后端",
            "department": "安全与风控",
            "url": "https://jobs.bytedance.com/campus/m/position/detail/7668323746595735861",
            "responsibilities": [
                "负责AI Agent相关后端系统的设计与开发",
                "构建大模型应用的服务端架构，支持高并发推理请求",
                "优化Agent工作流执行引擎，提升系统稳定性和响应速度",
                "参与大模型应用的全链路开发，从API设计到部署上线"
            ],
            "requirements": [
                "2027届本科及以上学历，计算机、软件工程、信息安全等相关专业优先",
                "至少熟悉一种主流编程语言（Go/C++/C/Rust/Java/Python/NodeJS等）",
                "有扎实的编程能力和良好的编码风格",
                "具备较强的逻辑思维与问题拆解能力",
                "有大模型应用开发或AI Agent项目经验者优先"
            ],
            "match_categories": ["AI大模型", "算法", "操作系统", "计算机网络", "数据库"],
            "match_tags": ["AI Agent", "大模型", "后端", "Go", "Python"]
        },
        # ========== 腾讯 ==========
        {
            "id": "tencent-backend-cpp",
            "company_id": "tencent",
            "company_name": "腾讯",
            "title": "后台开发工程师(C++)",
            "location": "深圳、北京、上海、广州",
            "salary": "25-45K",
            "job_type": "技术类",
            "department": "IEG/CSIG/TEG",
            "url": "https://join.qq.com/post.html",
            "responsibilities": [
                "负责腾讯后台服务的架构设计与开发",
                "构建高可用、高并发的分布式系统",
                "优化系统性能，解决线上疑难问题",
                "参与技术方案评审，推动技术演进"
            ],
            "requirements": [
                "计算机相关专业，本科及以上学历",
                "精通C++编程语言，熟悉STL、智能指针、多线程",
                "扎实的数据结构与算法基础，LeetCode中等以上水平",
                "熟悉TCP/IP、HTTP等网络协议，了解socket/epoll网络编程",
                "熟悉MySQL、Redis等存储组件",
                "了解分布式系统原理，有高并发系统开发经验者优先"
            ],
            "match_categories": ["C++", "算法", "操作系统", "计算机网络", "数据库"],
            "match_tags": ["C++", "后台开发", "分布式", "网络编程"]
        },
        # ========== 阿里巴巴 ==========
        {
            "id": "alibaba-java-backend",
            "company_id": "alibaba",
            "company_name": "阿里巴巴",
            "title": "Java开发工程师",
            "location": "杭州、北京、上海、深圳",
            "salary": "25-50K",
            "job_type": "技术类",
            "department": "淘宝/天猫/阿里云",
            "url": "https://campus.alibaba.com/positionList.htm",
            "responsibilities": [
                "负责阿里巴巴电商/云平台核心系统的后端开发",
                "参与高并发、高可用分布式系统的设计与实现",
                "优化系统性能，提升用户体验",
                "参与技术架构演进，推动技术创新"
            ],
            "requirements": [
                "计算机相关专业，本科及以上学历",
                "精通Java编程语言，熟悉JVM原理和性能调优",
                "熟悉Spring、Spring Boot、MyBatis等主流框架",
                "熟悉MySQL、Redis等存储组件，有SQL优化经验",
                "了解分布式系统原理，熟悉消息队列(Kafka/RocketMQ)",
                "扎实的数据结构与算法基础"
            ],
            "match_categories": ["Java", "算法", "数据库", "计算机网络", "操作系统"],
            "match_tags": ["Java", "Spring", "分布式", "MySQL", "JVM"]
        },
        # ========== 京东 ==========
        {
            "id": "jd-backend-java",
            "company_id": "jd",
            "company_name": "京东",
            "title": "后端开发工程师(Java)",
            "location": "北京、上海、深圳、成都",
            "salary": "20-40K",
            "job_type": "技术类",
            "department": "京东零售/京东物流",
            "url": "https://campus.jd.com/",
            "responsibilities": [
                "负责京东电商/物流平台的后端服务开发",
                "参与高并发交易系统、订单系统的设计与实现",
                "优化系统性能和稳定性",
                "参与技术方案讨论，解决疑难问题"
            ],
            "requirements": [
                "计算机相关专业，本科及以上学历",
                "熟练掌握Java编程语言，熟悉多线程和并发编程",
                "熟悉Spring、Spring Boot、MyBatis等框架",
                "熟悉MySQL、Oracle等关系型数据库及SQL优化",
                "熟悉Redis、Memcached等NoSQL解决方案",
                "了解分布式系统原理，熟悉消息队列(Kafka/RabbitMQ)",
                "扎实的数据结构与算法基础"
            ],
            "match_categories": ["Java", "算法", "数据库", "计算机网络", "操作系统"],
            "match_tags": ["Java", "Spring", "MySQL", "Redis", "分布式"]
        },
        # ========== 网易 ==========
        {
            "id": "netease-backend-java",
            "company_id": "netease",
            "company_name": "网易",
            "title": "后端开发工程师(Java)",
            "location": "杭州、广州",
            "salary": "20-40K",
            "job_type": "技术类",
            "department": "网易互娱/网易云音乐",
            "url": "https://campus.163.com/app/detail/index?id=3342&projectId=67",
            "responsibilities": [
                "负责网易游戏/音乐产品的后端服务开发",
                "参与高并发在线服务的架构设计与实现",
                "优化系统性能，保障服务稳定性",
                "参与技术方案评审，推动技术演进"
            ],
            "requirements": [
                "本科及以上学历，计算机相关专业",
                "扎实的Java编程基础，熟悉JVM原理和性能优化",
                "熟悉Spring Framework、Spring Boot、Spring Cloud等全家桶",
                "熟练使用Unix/Linux操作系统，熟悉RESTful API、Servlet、Tomcat",
                "熟悉MySQL、Redis等数据库的使用和优化",
                "了解Kafka等消息队列",
                "有分布式系统设计与调优能力者优先"
            ],
            "match_categories": ["Java", "算法", "数据库", "计算机网络", "操作系统"],
            "match_tags": ["Java", "Spring", "MySQL", "Redis", "JVM"]
        },
        {
            "id": "netease-game-cpp",
            "company_id": "netease",
            "company_name": "网易",
            "title": "游戏研发工程师(C++)",
            "location": "杭州、广州",
            "salary": "25-50K",
            "job_type": "技术类",
            "department": "网易互娱/雷火",
            "url": "https://campus.163.com/",
            "responsibilities": [
                "负责网易游戏客户端/服务端引擎开发",
                "参与游戏核心系统的设计与实现",
                "优化游戏性能，提升帧率和加载速度",
                "参与图形渲染、物理引擎等核心模块开发"
            ],
            "requirements": [
                "精通C++编程语言，熟悉C++11/14/17新特性",
                "熟悉数据结构与算法，有扎实的编程基础",
                "了解计算机图形学基础（渲染管线、Shader、OpenGL/D3D）",
                "熟悉游戏引擎（Unity/Unreal）者优先",
                "有游戏项目开发经验者优先"
            ],
            "match_categories": ["C++", "算法", "操作系统", "计算机网络"],
            "match_tags": ["C++", "游戏开发", "图形学", "引擎"]
        },
        # ========== 美团 ==========
        {
            "id": "meituan-backend-java",
            "company_id": "meituan",
            "company_name": "美团",
            "title": "后端开发工程师(Java)",
            "location": "北京、上海、深圳、成都",
            "salary": "20-40K",
            "job_type": "技术类",
            "department": "美团外卖/到店/基础架构",
            "url": "https://campus.meituan.com/",
            "responsibilities": [
                "负责美团外卖/到店核心业务系统的后端开发",
                "参与高并发交易系统、配送系统的设计与实现",
                "优化系统性能，保障大促期间服务稳定性",
                "参与技术架构演进，推动技术创新"
            ],
            "requirements": [
                "计算机相关专业，本科及以上学历",
                "熟练掌握Java编程语言，熟悉JVM原理",
                "熟悉Spring、Spring Boot等框架",
                "熟悉MySQL、Redis等存储组件",
                "了解分布式系统原理，熟悉消息队列",
                "扎实的数据结构与算法基础，LeetCode中等以上水平"
            ],
            "match_categories": ["Java", "算法", "数据库", "计算机网络", "操作系统"],
            "match_tags": ["Java", "Spring", "MySQL", "Redis", "分布式"]
        },
        # ========== 华为 ==========
        {
            "id": "huawei-cpp-dev",
            "company_id": "huawei",
            "company_name": "华为",
            "title": "C++开发工程师",
            "location": "深圳、东莞、北京、上海、杭州",
            "salary": "20-45K",
            "job_type": "研发类",
            "department": "2012实验室/消费者BG/运营商BG",
            "url": "https://career.huawei.com/reccampportal/",
            "responsibilities": [
                "负责华为操作系统/编译器/数据库等基础软件的开发",
                "参与分布式系统、云原生平台的设计与实现",
                "优化系统性能，提升产品竞争力",
                "参与技术预研，跟踪前沿技术"
            ],
            "requirements": [
                "计算机相关专业，本科及以上学历",
                "精通C/C++编程语言，熟悉数据结构与算法",
                "熟悉Linux系统编程，了解操作系统原理",
                "熟悉TCP/IP网络协议，有网络编程经验者优先",
                "有编译器/操作系统/数据库相关项目经验者优先",
                "英语CET-4以上，能阅读英文技术文档"
            ],
            "match_categories": ["C++", "算法", "操作系统", "计算机网络", "数据库"],
            "match_tags": ["C++", "Linux", "系统编程", "分布式"]
        },
        # ========== 小米 ==========
        {
            "id": "xiaomi-backend-python",
            "company_id": "xiaomi",
            "company_name": "小米",
            "title": "后端开发工程师(Python/Go)",
            "location": "北京、上海、深圳",
            "salary": "20-40K",
            "job_type": "技术类",
            "department": "小米汽车/IoT/互联网业务",
            "url": "https://hr.xiaomi.com/campus",
            "responsibilities": [
                "负责小米IoT/汽车/互联网业务的后端服务开发",
                "参与高并发设备接入平台、数据平台的设计与实现",
                "优化系统性能，保障海量设备连接稳定性",
                "参与技术方案讨论，推动技术演进"
            ],
            "requirements": [
                "计算机相关专业，本科及以上学历",
                "熟练掌握Python/Go至少一种编程语言",
                "扎实的数据结构与算法基础",
                "熟悉TCP/IP、HTTP、MQTT等网络协议",
                "熟悉MySQL、Redis、MongoDB等存储组件",
                "了解分布式系统原理，有高并发系统开发经验者优先",
                "有IoT/汽车相关项目经验者优先"
            ],
            "match_categories": ["Python", "算法", "操作系统", "计算机网络", "数据库"],
            "match_tags": ["Python", "Go", "IoT", "分布式", "MQTT"]
        },
        # ========== 百度 ==========
        {
            "id": "baidu-ai-algorithm",
            "company_id": "baidu",
            "company_name": "百度",
            "title": "AI算法工程师(大模型方向)",
            "location": "北京、上海、深圳",
            "salary": "30-60K",
            "job_type": "技术类",
            "department": "文心一言/百度搜索/阿波罗",
            "url": "https://talent.baidu.com/external/baidu/campus.html",
            "responsibilities": [
                "负责百度文心大模型的预训练、微调与优化",
                "参与大模型推理加速、模型压缩等技术研发",
                "构建大模型应用的算法 pipeline，支持业务落地",
                "跟踪前沿技术，发表顶会论文"
            ],
            "requirements": [
                "计算机/数学/统计相关专业，硕士及以上学历优先",
                "扎实的机器学习/深度学习基础，熟悉Transformer架构",
                "熟练使用PyTorch/TensorFlow等深度学习框架",
                "有大模型预训练/微调经验者优先",
                "有分布式训练经验（DeepSpeed/Megatron）者优先",
                "在NeurIPS/ICML/ACL等顶会发表论文者优先",
                "扎实的编程基础（Python/C++）"
            ],
            "match_categories": ["AI大模型", "算法", "Python", "操作系统"],
            "match_tags": ["大模型", "Transformer", "深度学习", "NLP", "分布式训练"]
        }
    ]
}

# 保存
with open('data/positions.json', 'w', encoding='utf-8') as f:
    json.dump(positions, f, ensure_ascii=False, indent=2)

print(f'Created positions.json with {len(positions["positions"])} positions')
for p in positions['positions']:
    print(f'  {p["company_name"]:6} | {p["title"]:30} | {p["location"]}')
