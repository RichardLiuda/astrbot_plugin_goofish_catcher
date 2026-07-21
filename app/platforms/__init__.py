"""多平台适配层（阶段 0.2 起）。

- registry：item_id 的平台归属解析与商品 URL 构建，全项目唯一收口点。
- base / goofish：SiteProfile 站点档案与闲鱼档案（阶段 0.3a），
  通用抓取引擎与登录会话经此读取平台特数据。
- taobao：淘宝档案（阶段 1.1，SSR 页面走 DOM 定制提取钩子）。
"""

from .base import SiteProfile
from .goofish import GOOFISH_PROFILE
from .registry import (
    PLATFORM_TAOBAO,
    build_item_url,
    make_item_id,
    platform_display_name,
    split_item_id,
)
from .taobao import TAOBAO_PROFILE

__all__ = [
    "GOOFISH_PROFILE",
    "PLATFORM_TAOBAO",
    "SiteProfile",
    "TAOBAO_PROFILE",
    "build_item_url",
    "make_item_id",
    "platform_display_name",
    "split_item_id",
]
