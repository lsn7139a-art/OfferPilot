# OfferPilot 部署指南

## GitHub Action 部署

### 1. 配置 Secrets

打开仓库 Settings → Secrets and variables → Actions → New repository secret，添加以下4个：

| Secret 名称 | 值 | 说明 |
|---|---|---|
| `FEISHU_APP_ID` | `cli_aa83de05f7395bb4` | 飞书自建应用 App ID |
| `FEISHU_APP_SECRET` | 你的应用 App Secret | 飞书自建应用 App Secret |
| `FEISHU_CHAT_ID` | `oc_206bb0c8dd9428916ad9bfb3461a8074` | 飞书群「lsn」的 chat_id |
| `FEISHU_USER_OPEN_ID` | `ou_5d5bd9ee067b7c8a71dc2a7828f8f9ae` | 你的飞书 open_id |

### 2. 飞书应用权限

确保应用已开通以下权限：
- `im:message` — 发送消息
- `im:chat` — 群管理
- `task:task:write` — 创建/更新待办任务
- `contact:user.id:readonly` — 查询用户ID

### 3. Workflow 说明

| Workflow | 触发时间 | 功能 |
|---|---|---|
| `daily-push.yml` | 每天北京时间 9:00 | 推送岗位+3道题到群，创建3个独立待办 |
| `evening-reminder.yml` | 每天北京时间 21:00 | 发送晚间学习提醒 |

### 4. 手动触发

在仓库 Actions 页面，选择对应的 workflow，点击「Run workflow」可手动触发。

### 5. 核心逻辑

- 每天推送前自动检测昨日待办完成状态
- **未完成的题目** → 延期（更新截止日期到今天），只换岗位
- **已完成的题目** → 替换成新题，创建新待办
- 保证每天3道题，岗位每天换新
- 在飞书待办里点「完成」即可，系统自动检测

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 每日推送（群消息+待办）
python scripts/feishu_push.py --mode daily

# 晚间提醒
python scripts/feishu_push.py --mode evening

# 测试消息
python scripts/feishu_push.py --mode test
```

## 项目结构

```
OfferPilot/
├── config.json              # 本地配置（含secret，不提交）
├── config.example.json      # 配置模板
├── requirements.txt         # Python依赖
├── data/
│   ├── questions.json       # 92题题库
│   ├── companies.json       # 10家公司JD
│   ├── positions.json       # 15个具体岗位
│   ├── progress.json        # 学习进度
│   └── daily_log.json       # 每日推送日志
├── scripts/
│   ├── feishu_api.py        # 飞书API封装
│   ├── feishu_push.py       # 飞书推送主脚本
│   ├── daily_push.py        # 每日选题+消息生成
│   ├── progress_sync.py     # 进度同步Agent
│   └── update_questions.py  # 题库更新
└── .github/workflows/
    ├── daily-push.yml       # 每日推送
    └── evening-reminder.yml # 晚间提醒
```
