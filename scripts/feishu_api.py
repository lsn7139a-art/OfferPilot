#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书API封装模块
- 直接调用飞书开放平台API，不依赖lark-cli
- 支持：获取tenant_access_token、发送群消息、创建待办任务
"""

import json
import os
import time
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 飞书API基础URL
FEISHU_BASE = "https://open.feishu.cn/open-apis"

# token缓存
_token_cache = {"token": None, "expire_time": 0}


def load_config():
    """加载配置"""
    config_path = os.path.join(BASE_DIR, 'config.json')
    with open(config_path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def get_tenant_access_token():
    """获取tenant_access_token（带缓存）"""
    now = time.time()
    if _token_cache["token"] and _token_cache["expire_time"] > now + 60:
        return _token_cache["token"]

    config = load_config()
    feishu = config.get('feishu', {})
    app_id = feishu.get('app_id', '')
    app_secret = feishu.get('app_secret', '')

    if not app_id or not app_secret:
        raise ValueError("飞书app_id或app_secret未配置")

    url = f"{FEISHU_BASE}/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret})
    data = resp.json()

    if data.get("code") != 0:
        raise Exception(f"获取token失败: {data.get('msg')}")

    token = data["tenant_access_token"]
    expire = data.get("expire", 7200)
    _token_cache["token"] = token
    _token_cache["expire_time"] = now + expire
    return token


def get_headers():
    """获取带token的请求头"""
    token = get_tenant_access_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


def send_message_to_chat(chat_id, text):
    """
    发送文本消息到飞书群
    :param chat_id: 群ID
    :param text: 消息文本
    :return: message_id
    """
    url = f"{FEISHU_BASE}/im/v1/messages"
    body = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    resp = requests.post(url, headers=get_headers(), params={"receive_id_type": "chat_id"}, json=body)
    data = resp.json()

    if data.get("code") != 0:
        raise Exception(f"发送消息失败: {data.get('msg')}")

    return data.get("data", {}).get("message_id", "")


def create_task(summary, description, assignee_open_id, due_timestamp=None, is_all_day=True):
    """
    创建飞书待办任务
    :param summary: 任务标题
    :param description: 任务描述
    :param assignee_open_id: 负责人open_id
    :param due_timestamp: 截止时间戳（秒），默认明天
    :param is_all_day: 是否全天任务
    :return: task_guid
    """
    if due_timestamp is None:
        # 默认今天23:59:59截止（北京时间）
        from time_utils import get_today_end_timestamp
        due_timestamp = get_today_end_timestamp()

    # 飞书API需要毫秒级时间戳
    due_timestamp_ms = str(due_timestamp * 1000)

    url = f"{FEISHU_BASE}/task/v2/tasks"
    body = {
        "summary": summary,
        "description": description,
        "due": {
            "timestamp": due_timestamp_ms,
            "is_all_day": is_all_day
        },
        "members": [
            {
                "id": assignee_open_id,
                "type": "user",
                "role": "assignee"
            }
        ]
    }
    resp = requests.post(url, headers=get_headers(), json=body)
    data = resp.json()

    if data.get("code") != 0:
        raise Exception(f"创建任务失败: {data.get('msg')}")

    return data.get("data", {}).get("task", {}).get("guid", "")


def get_task(task_guid):
    """
    获取飞书任务详情（含状态）
    :param task_guid: 任务GUID
    :return: 任务对象dict，包含status字段（todo/done等）
    """
    url = f"{FEISHU_BASE}/task/v2/tasks/{task_guid}"
    resp = requests.get(url, headers=get_headers())
    data = resp.json()

    if data.get("code") != 0:
        raise Exception(f"查询任务失败: {data.get('msg')}")

    return data.get("data", {}).get("task", {})


def get_task_status(task_guid):
    """Return the Feishu task status or raise when lookup fails."""
    return get_task(task_guid).get("status", "unknown")


def update_task_due(task_guid, due_timestamp, is_all_day=True):
    """
    更新任务截止日期（用于延期未完成任务）
    :param task_guid: 任务GUID
    :param due_timestamp: 新的截止时间戳（秒）
    :param is_all_day: 是否全天任务
    """
    url = f"{FEISHU_BASE}/task/v2/tasks/{task_guid}"
    body = {
        "update_fields": ["due"],
        "task": {
            "due": {
                "timestamp": str(due_timestamp * 1000),  # 毫秒
                "is_all_day": is_all_day
            }
        }
    }
    resp = requests.patch(url, headers=get_headers(), json=body)
    data = resp.json()

    if data.get("code") != 0:
        raise Exception(f"更新任务截止日期失败: {data.get('msg')}")

    return True


def delete_task(task_guid):
    """
    删除任务（用于清理昨天的旧任务）
    :param task_guid: 任务GUID
    """
    url = f"{FEISHU_BASE}/task/v2/tasks/{task_guid}"
    resp = requests.delete(url, headers=get_headers())
    data = resp.json()

    if data.get("code") != 0:
        # 任务可能已经被删除或不存在，不抛出异常
        print(f"⚠️ 删除任务失败（可能已删除）: {data.get('msg')}")
        return False

    return True


def get_user_open_id_by_mobile(mobile):
    """通过手机号获取用户open_id"""
    url = f"{FEISHU_BASE}/contact/v3/users/batch_get_id"
    body = {"mobiles": [mobile]}
    resp = requests.post(url, headers=get_headers(), json=body)
    data = resp.json()

    if data.get("code") != 0:
        raise Exception(f"查询用户失败: {data.get('msg')}")

    users = data.get("data", {}).get("user_list", [])
    if users:
        return users[0].get("user_id", "")
    return ""


def create_chat(name, owner_open_id):
    """
    创建飞书群
    :param name: 群名
    :param owner_open_id: 群主open_id
    :return: chat_id
    """
    url = f"{FEISHU_BASE}/im/v1/chats"
    body = {
        "name": name,
        "user_id_type": "open_id",
        "owner_id": owner_open_id,
        "chat_mode": "group",
        "chat_type": "private"
    }
    resp = requests.post(url, headers=get_headers(), json=body)
    data = resp.json()

    if data.get("code") != 0:
        raise Exception(f"创建群失败: {data.get('msg')}")

    return data.get("data", {}).get("chat_id", "")


if __name__ == '__main__':
    # 测试
    config = load_config()
    feishu = config.get('feishu', {})
    print(f"群名: {feishu.get('chat_name')}")
    print(f"群ID: {feishu.get('chat_id')}")
    print(f"用户open_id: {feishu.get('user_open_id')}")

    # 测试获取token
    token = get_tenant_access_token()
    print(f"token获取成功: {token[:20]}...")
