# 闲鱼插件技能总览

本目录是插件全部操作技能的单一来源，供两层 agent 使用：

- **AstrBot 主 LLM agent**（用户直接对话的 AI）：决定调哪个 `@llm_tool`
- **GofishBrowserAgent**（`app/browser_agent.py`）：决定每步执行哪个浏览器动作

---

## 快速决策树（主 LLM agent）

```
用户想要...
├── 想买/比价/蹲好价/模糊需求    → buyagent_purchase_decision  → skills/purchase.md
│   （"帮我看看红色5090""预算1万5买啥"）
├── 搜索/查询行情（仅闲鱼）      → goofish_search_live          → skills/search.md
├── 收藏商品
│   ├── 从搜索结果收藏   → 引用回复序号（无需工具）    → skills/favorite.md
│   └── 收藏指定链接     → goofish_browser_task         → skills/agent.md
├── 订阅/监控
│   ├── 新建监控         → goofish_create_subscription  → skills/subscribe.md
│   │   （淘宝订阅加 platform="taobao"，见 skills/platforms.md）
│   ├── 管理已有订阅     → goofish_*_subscription       → skills/subscribe.md
│   └── 立即触发检查     → goofish_check_subscription   → skills/subscribe.md
├── 查看历史数据         → goofish_list_items            → skills/data-and-status.md
├── 查商品详情           → goofish_get_item_detail       → skills/data-and-status.md
│   （淘宝商品用 goofish_analyze_item_detail，有 SKU 全档真实价）
├── 系统状态/登录        → goofish_get_overview /        → skills/data-and-status.md
│                          goofish_check_login /
│                          goofish_start_login
│                          （均支持 platform 参数，默认闲鱼）
├── 多平台机制说明       → skills/platforms.md（淘宝能力/限制/数据真相）
└── 复杂浏览器操作       → goofish_browser_task          → skills/agent.md
```

---

## 全部工具速查（主 LLM agent）

| 工具名 | 功能 | 详细文档 |
|--------|------|----------|
| `buyagent_purchase_decision` | 采购决策卡片：多平台并发+降级+聚合（第 18 个工具） | [purchase.md](purchase.md) |
| `goofish_search_live` | 实时搜索（仅闲鱼），发出可收藏格式的结果列表 | [search.md](search.md) |
| `goofish_browser_task` | 浏览器 Agent 执行复杂页面操作 | [agent.md](agent.md) |
| `goofish_list_subscriptions` | 查看订阅列表 | [subscribe.md](subscribe.md) |
| `goofish_create_subscription` | 新建关键词监控订阅（`platform` 参数支持淘宝） | [subscribe.md](subscribe.md) |
| `goofish_update_subscription` | 修改订阅参数 | [subscribe.md](subscribe.md) |
| `goofish_delete_subscription` | 删除订阅 | [subscribe.md](subscribe.md) |
| `goofish_pause_subscription` | 暂停订阅 | [subscribe.md](subscribe.md) |
| `goofish_resume_subscription` | 恢复订阅 | [subscribe.md](subscribe.md) |
| `goofish_check_subscription` | 立即执行一次订阅检查 | [subscribe.md](subscribe.md) |
| `goofish_list_items` | 查询本地缓存商品数据库 | [data-and-status.md](data-and-status.md) |
| `goofish_get_item_detail` | 查单个商品详情+价格历史 | [data-and-status.md](data-and-status.md) |
| `goofish_get_overview` | 插件运行状态概览 | [data-and-status.md](data-and-status.md) |
| `goofish_check_login` | 检查会话状态（`platform` 参数，默认闲鱼） | [data-and-status.md](data-and-status.md) |
| `goofish_start_login` | 启动登录流程（`platform` 参数支持淘宝） | [data-and-status.md](data-and-status.md) |

多平台机制（能力矩阵/淘宝数据真相/会话隔离）见 [platforms.md](platforms.md)。

---

## 浏览器 Agent 动作速查（GofishBrowserAgent）

完整文档见 [agent.md](agent.md)。

| 动作 | 场景 |
|------|------|
| `navigate` | 第一步跳转目标 URL |
| `extract_items` | 搜索页到达后立即提取商品，无需 LLM 逐条解析 |
| `click` | 点击收藏按钮、链接等 |
| `scroll` | 触发懒加载 |
| `wait` | 等待动态内容 |
| `extract` | 从 AX 树提取特定信息（extract_items 不适用时） |
| `done` | 返回结果 |
| `fail` | 遇到登录墙/验证码时终止 |

**标准搜索（3 步）**：`navigate` → `extract_items` → `done`  
**标准收藏（3 步）**：`navigate` 详情页 → `click "收藏"` → `done`

---

## 关键规则

1. **搜索用 `goofish_search_live`**（仅闲鱼），不用 `goofish_browser_task`（慢 10 倍）；**比价/模糊需求用 `buyagent_purchase_decision`**（多平台并发）
2. **搜索结果支持引用回复收藏**：发出后用户回复序号即触发，无需工具；**淘宝商品收藏暂不支持**（会提示并跳过）
3. **会话过期统一处理**：所有工具遇到 `AUTH_REQUIRED` → 闲鱼提示 `/闲鱼 登录`，淘宝提示"淘宝登录"（`goofish_start_login(platform="taobao")`）
4. **平台参数**：`goofish_create_subscription` / `goofish_check_login` / `goofish_start_login` 均带 `platform`（默认 `goofish`，淘宝传 `taobao`）；用户说"订阅淘宝的X"时必须传 `platform="taobao"`
5. **复杂页面操作**（详情页/收藏指定链接）→ `goofish_browser_task`
6. **浏览器 Agent 内**：搜索页到达后首选 `extract_items`，不要用 LLM 读 AX 树逐条解析商品
