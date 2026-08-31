#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北京时间工具模块
统一所有脚本的时间获取，确保在UTC服务器（GitHub Action）上也能正确获取北京时间
"""

import os
from datetime import datetime, timedelta, timezone

# 北京时间 UTC+8
BEIJING_TZ = timezone(timedelta(hours=8))


def get_now():
    """获取当前北京时间（datetime对象）"""
    return datetime.now(BEIJING_TZ)


def get_today_date():
    """获取今日日期字符串（YYYY-MM-DD，北京时间）"""
    return get_now().strftime('%Y-%m-%d')


def get_weekday_cn():
    """获取今日星期几（中文，北京时间）"""
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return weekdays[get_now().weekday()]


def get_today_end_timestamp():
    """获取今日23:59:59的时间戳（秒，北京时间）"""
    now = get_now()
    today_end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    return int(today_end.timestamp())


def get_isoformat():
    """获取当前时间的ISO格式字符串（北京时间）"""
    return get_now().isoformat()


def set_timezone():
    """
    设置系统时区为北京时间（仅Linux/macOS有效）
    在GitHub Action等UTC环境下调用，确保datetime.now()返回北京时间
    """
    os.environ['TZ'] = 'Asia/Shanghai'
    try:
        import time
        time.tzset()
    except AttributeError:
        pass  # Windows不支持tzset，但Windows本地时区通常已是北京时间


# 模块加载时自动设置时区
set_timezone()
