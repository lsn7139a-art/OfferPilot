# GitHub Action 部署指南

## 项目结构

```
interview-prep/
├── .github/workflows/
│   ├── daily-push.yml       # 每日9点推送（群消息+飞书待办）
│   └── evening-reminder.yml # 每日21点晚间提醒
├── data/
│   ├── questions.json        # 92道面试题
│   ├── positions.json        # 15个具体岗位（含精确URL）
│   ├── companies.json        # 10家公司详细JD
│   └── config.json           # 系统配置
├── scripts/
│   ├── daily_push.py         # 智能选题+消息生成
│   ├── feishu_push.py        # 飞书推送（群消息+待办任务）
│   ├── create_daily_task.py  # 创建飞书每日待办
│   └── progress_sync.py      # 进度同步Agent
└── README.md
```

## 部署步骤

### 1. 创建GitHub仓库

```bash
cd interview-prep
git init
git add .
git commit -m "init: 面试题准备系统"
git branch -M main
git remote add origin https://github.com/你的用户名/interview-prep.git
git push -u origin main
```

### 2. 配置GitHub Secrets

在GitHub仓库 → Settings → Secrets and variables → Actions → New repository secret：

**Name:** `LARK_CLI_CONFIG`

**Value:** 你本地 `~/.lark-cli/config.json` 文件的完整内容

获取方式（在本地执行）：
```bash
# Windows PowerShell
Get-Content "$env:USERPROFILE\.lark-cli\config.json" -Raw

# Mac/Linux
cat ~/.lark-cli/config.json
```

把输出的完整JSON复制粘贴到Secret的Value中。

### 3. 测试Workflow

1. 进入GitHub仓库 → Actions
2. 选择「每日面试题推送」
3. 点击「Run workflow」手动触发
4. 等待执行完成，查看飞书群是否收到消息

### 4. 定时任务说明

| Workflow | 触发时间 | 功能 |
|----------|----------|------|
| daily-push | 每天 9:00（北京时间） | 推送岗位+3道题到飞书群，同时创建飞书待办 |
| evening-reminder | 每天 21:00（北京时间） | 发送晚间学习提醒 |

> 注意：GitHub Action的cron使用UTC时间，北京时间9:00 = UTC 1:00

## 重要注意事项

### Token过期问题

lark-cli的 `user_access_token` 有效期约2小时，`refresh_token` 有效期约30天。

**当推送失败时**，大概率是token过期了，需要：
1. 在本地重新运行 `lark-cli` 相关命令触发登录刷新
2. 重新复制 `~/.lark-cli/config.json` 内容
3. 更新GitHub Secret `LARK_CLI_CONFIG`

建议每月检查更新一次token。

### 飞书群ID

当前配置的飞书群ID在 `scripts/feishu_push.py` 中：
```python
FEISHU_CHAT_ID = "oc_839d3dac5ee30f5f118c66b8f5793539"
```

如果需要换群，修改这个ID即可。

### 题库更新

题库数据在 `data/questions.json`、`data/positions.json`、`data/companies.json` 中。

更新方式：
1. 直接编辑JSON文件添加新题目/岗位
2. git commit + push
3. GitHub Action会自动使用最新数据

## 本地调试

```bash
# 生成每日推送消息（不发送）
python scripts/daily_push.py

# 发送到飞书群（同时创建待办）
python scripts/feishu_push.py --mode daily

# 发送晚间提醒
python scripts/feishu_push.py --mode evening

# 仅创建飞书待办任务
python scripts/create_daily_task.py
```
