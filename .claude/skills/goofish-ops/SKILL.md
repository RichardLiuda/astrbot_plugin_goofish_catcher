---
name: goofish-ops
description: 闲鱼插件操作指南——搜索商品、收藏商品、管理订阅、查询数据、浏览器 Agent。在用户询问如何搜索、收藏、监控闲鱼商品，或需要调用相关 LLM 工具时自动加载。
---

# 闲鱼插件 LLM 工具操作指南

详细文档在 `docs/skills/` 目录（与插件代码并列）：

- [総覧 & 決策树](../../../skills/README.md)
- [搜索商品](../../../skills/search.md) — `goofish_search_live`
- [收藏商品](../../../skills/favorite.md) — 引用回复 / `goofish_browser_task`
- [订阅管理](../../../skills/subscribe.md) — `goofish_*_subscription`
- [浏览器 Agent](../../../skills/agent.md) — `goofish_browser_task`
- [数据查询与系统状态](../../../skills/data-and-status.md) — `goofish_list_items` 等

## 核心规则（速查）

1. **搜索** → `goofish_search_live`（不用 browser_task）
2. **搜索结果支持引用回复收藏**：发出后用户回复序号即可触发收藏
3. **会话过期** → 提示 `/闲鱼 登录`
4. **复杂页面操作**（详情页/收藏指定链接）→ `goofish_browser_task`

## 开发者调试

见 [.claude/skills/run-goofish-scraper/SKILL.md](../run-goofish-scraper/SKILL.md)
