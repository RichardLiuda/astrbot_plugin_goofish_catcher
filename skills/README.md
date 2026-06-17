# 技能总览：闲鱼插件 LLM 工具

本目录是插件全部 LLM 工具的操作指南，按功能域分组。

## 快速决策树

```
用户想要...
├── 搜索/查询行情        → goofish_search_live          → docs/skills/search.md
├── 收藏商品
│   ├── 从搜索结果收藏   → 引用回复序号（无需工具）    → docs/skills/favorite.md
│   └── 收藏指定链接     → goofish_browser_task         → docs/skills/agent.md
├── 订阅/监控
│   ├── 新建监控         → goofish_create_subscription  → docs/skills/subscribe.md
│   ├── 管理已有订阅     → goofish_*_subscription       → docs/skills/subscribe.md
│   └── 立即触发检查     → goofish_check_subscription   → docs/skills/subscribe.md
├── 查看历史数据         → goofish_list_items            → docs/skills/data-and-status.md
├── 查商品详情           → goofish_get_item_detail       → docs/skills/data-and-status.md
├── 系统状态/登录        → goofish_get_overview /        → docs/skills/data-and-status.md
│                          goofish_check_login /
│                          goofish_start_login
└── 复杂浏览器操作       → goofish_browser_task          → docs/skills/agent.md
```

## 全部工具速查

| 工具名 | 功能 | 详细文档 |
|--------|------|----------|
| `goofish_search_live` | 实时搜索，发出可收藏格式的结果列表 | [search.md](search.md) |
| `goofish_browser_task` | 浏览器 Agent 执行复杂页面操作 | [agent.md](agent.md) |
| `goofish_list_subscriptions` | 查看订阅列表 | [subscribe.md](subscribe.md) |
| `goofish_create_subscription` | 新建关键词监控订阅 | [subscribe.md](subscribe.md) |
| `goofish_update_subscription` | 修改订阅参数 | [subscribe.md](subscribe.md) |
| `goofish_delete_subscription` | 删除订阅 | [subscribe.md](subscribe.md) |
| `goofish_pause_subscription` | 暂停订阅 | [subscribe.md](subscribe.md) |
| `goofish_resume_subscription` | 恢复订阅 | [subscribe.md](subscribe.md) |
| `goofish_check_subscription` | 立即执行一次订阅检查 | [subscribe.md](subscribe.md) |
| `goofish_list_items` | 查询本地缓存商品数据库 | [data-and-status.md](data-and-status.md) |
| `goofish_get_item_detail` | 查单个商品详情+价格历史 | [data-and-status.md](data-and-status.md) |
| `goofish_get_overview` | 插件运行状态概览 | [data-and-status.md](data-and-status.md) |
| `goofish_check_login` | 检查闲鱼会话状态 | [data-and-status.md](data-and-status.md) |
| `goofish_start_login` | 启动登录流程 | [data-and-status.md](data-and-status.md) |

## 关键规则

1. **搜索用 `goofish_search_live`**，不用 `goofish_browser_task`
2. **搜索结果格式支持回复收藏**：`goofish_search_live` 发出的列表，用户引用后回复序号即可触发收藏
3. **会话过期统一处理**：所有工具遇到 `AUTH_REQUIRED` → 提示用户 `/闲鱼 登录`
4. **数据库查询 vs 实时搜索**：`goofish_list_items` 查本地缓存，`goofish_search_live` 实时爬取
