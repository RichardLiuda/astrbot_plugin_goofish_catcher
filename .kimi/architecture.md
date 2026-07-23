# 架构与数据流（截至 v3.6.0 + 阶段 0.1 改造）

> 范式：每个模块对应什么功能、数据从哪进从哪出、涉及哪些表/字段、用户动作如何流转到这一层。

## 一句话定位

AstrBot 插件「闲鱼蹲蹲助手」：LLM 工具调用 + 关键词订阅监控 + LLM 推荐排序。
**正在改造为多平台采购决策 Agent**（淘宝优先，见 roadmap.md）。

## 部署形态（provider_mode，与电商平台无关）

- `playwright_local`：插件进程内跑 Chromium（`PlaywrightSearchProvider`）
- `remote_rest`：AstrBot 侧 `RemoteSearchProvider` → HTTP → 远端 `worker_server.py`（FastAPI）里的 `PlaywrightSearchProvider`

## 模块地图（app/）

| 文件 | 功能 | 数据进 → 出 |
|---|---|---|
| `provider.py` | `SearchProvider` Protocol + `build_provider`（单平台，兼容保留）+ `build_providers`（平台路由表 dict，1.5b 起：淘宝独立会话目录，远程模式跳过） | settings → dict[platform, provider] |
| `provider_playwright.py` | 核心抓取引擎：真实 Chromium 渲染 + XHR 嗅探；平台特数据全部读 `self._profile`（0.3a 起）；`analyze_item_detail` 对 `supports_item_detail=False` 的平台短路（1.5b 起） | keyword → `list[NormalizedItem]`；cookie 从 storage_state.json/browser_profile 进，操作后回写 |
| `provider_remote.py` | 远程模式的 HTTP 客户端 | SearchProvider 调用 → REST `/v1/*` |
| `provider_retry.py` | 仅 CAPTCHA 重试（≤2 次，间隔 1s） | — |
| `intent/engine.py` | 意图引擎：LLM 拆解自然语言→关键词/属性/预算/降级阶梯，启发式兜底（2.x 起） | 文本 → PurchaseIntent（llm_call 可注入，失败必回退） |
| `aggregator/aggregate.py` | 决策聚合：平台内去重、风险标签（按平台规则）、LLM/启发式排序 | 候选 → DecisionItem 列表 + summary |
| `reporter/card.py` | Markdown 决策卡片渲染（降级提示/平台分节/"N 条未进推荐"/失败节） | DecisionReport → 纯文本卡片 |
| `purchase.py` | `PurchaseDecisionService`：并发搜索→逐级降级→聚合排序的编排（2.x 起） | requirement 文本 → DecisionReport；单平台 20s 超时+异常隔离 |
| `provider_agent.py` | LLM 兜底提取（AX 树→商品/登录态/收藏按钮） | AX 文本 + llm_call → JSON |
| `browser_agent.py` | `GofishBrowserAgent`：独立 Chromium 的 ReAct 循环，对应 llm_tool `goofish_browser_task` | task 描述 → 多步浏览器动作 |
| `types.py` | 全部领域 dataclass + ProviderError | `DEFAULT_PLATFORM="goofish"`（阶段 0.1 起） |
| `platforms/` | 多平台适配层：`registry.py`=item_id 归属+商品 URL+URL 工具收口；`base.py`=`SiteProfile`（21 数据字段+6 钩子，含可选 `parse_dom_card`/`dom_card_extractor_js`）；`goofish.py`=闲鱼档案；`taobao.py`=淘宝档案（SSR→DOM 定制提取，1.1 已验证） | provider_playwright 经 profile 读平台特数据，新平台只加档案 |
| `config.py` | `PluginSettings` 加载（AstrBot config + admin_runtime_config.json overlay，overlay 永远赢） | dict → 强类型 settings |
| `storage.py` | `SubscriptionStorage`（aiosqlite + WAL + 写锁 + user_version 迁移） | 见下方 DB schema |
| `scheduler.py` | `MonitoringScheduler`：自研 asyncio 队列轮询订阅；**按 `sub.platform` 路由 provider**（dict 注入，1.5b 起；无 provider 时 PLATFORM_UNAVAILABLE 暂停+告警）；深度分析按 item_id 前缀路由 | 到期订阅 → 搜索 → 检测 → 推荐 → 通知；写 items/price_history/market_price/notifications |
| `detector.py` | 上新/降价判定纯函数 | 价格序列 → NEW/PRICE_DROP 决策 |
| `recommender.py` | `GoofishRecommender`：LLM 预筛 + LLM 排序（启发式兜底） | 候选 → RecommendationResult |
| `notifier.py` | 出站消息（`context.send_message(umo)` + webhook） | RecommendationResult → MessageChain |
| `auth_session.py` / `login_session.py` | 扫码登录编排 / 登录会话（**均按平台注入 SiteProfile**，P0 起）：taobao 用 login.taobao.com 落地页 + mtop.user.getusersimple 校验 | 二维码截图 ↔ storage_state.{platform}.json + browser_profile_{platform}/ |
| `remote_auth_recovery.py` | 会话级登录恢复状态机（**按平台分 flow**，P0 起：淘宝订阅暂停→推淘宝二维码→只恢复淘宝订阅） | ProviderError + platform → 用户消息 → confirm |
| `admin_service.py` / `admin_server.py` / `admin_types.py` | Admin WebUI facade + FastAPI（8790） | storage/scheduler → REST → Preact 前端 |
| `activity_monitor.py` | 内存态任务看板（admin 展示用） | — |
| `main.py` | **全部 17 个 llm_tool 必须在此**（AstrBot 校验 handler.__module__）+ 11 个 /闲鱼 子命令 + 引用收藏 | 用户消息 ↔ 上述全部组件 |

## 核心数据流

### 实时搜索（llm_tool `goofish_search_live`）
```
用户自然语言 → AstrBot LLM 调工具 → main.py → provider_retry → provider.search
  → Chromium 打开 goofish.com/search?q=（storage_state 注入 cookie）
  → 页面内 mtop SDK 自动签名 → h5api.m.goofish.com 返回 JSON
  → response 嗅探（主）/ DOM（备）/ AX+LLM（兜底）三级提取 → list[NormalizedItem]
  → 文本/合并转发消息发用户；llm_tool 返回值只是给 LLM 的摘要
```

### 订阅监控（scheduler._process_subscription）
```
到期订阅 → search_with_captcha_retry → 价格过滤 → filtered_items 去重 → LLM 预筛
  → upsert_market_price（EMA，键=(platform, keyword)，阶段 0.1 起）
  → detector：NEW（publish_time 窗口内）/ PRICE_DROP（绝对额或百分比阈值 + 冷却 + payload_hash 去重）
  → deep_analyze_candidates（前 3 个，详情页信用分析，6h 缓存，CAPTCHA 熔断 30min）
  → recommender.analyze（LLM 排序，启发式兜底）→ notifier.send_recommendation_summary
  → 发送成功才写 notifications 去重表
```

### 登录与恢复
```
AUTH_REQUIRED/CAPTCHA → remote_auth_recovery coordinator → 推送二维码截图
  → 用户扫码后回复任意消息 → validate_login（要求 loginuser.get + user.page.nav
    两个 mtop 接口成功）→ 保存 storage_state.json → 恢复被暂停订阅
日常保活 = 每次 provider 操作成功后回写 storage_state（无独立心跳）
```

### 引用收藏
```
用户引用「【闲鱼建议】/【查询推荐】/【立即检查】」消息回复序号
  → 三个事件钩子（main.py）→ reply_favorite.py 解析序号↔URL（正则认 `链接：` 行）
  → provider.favorite_item（详情页点收藏按钮，等文本变"已收藏"）
```

## DB schema（goofish_catcher.db，user_version=7）

| 表 | 主键/唯一键 | 要点 | 写入方 |
|---|---|---|---|
| subscriptions | UNIQUE(umo, **platform**, keyword)（v7 起） | 订阅参数+闲鱼专属过滤列；platform 默认 'goofish' | /闲鱼 订阅、llm_tool、Admin |
| items | UNIQUE(sub_id, item_id) | item_id 目前=闲鱼数字 ID（裸用，多平台撞号风险，0.2 处理） | scheduler |
| price_history | (item_id, observed_at) 索引 | 每次观测都写；source 列=provider_mode | scheduler |
| notifications | UNIQUE(sub_id,item_id,event_type,payload_hash) | 发送成功才写，漏发有补偿逻辑 | scheduler |
| fetch_runs | — | 每次抓取运行记录 | scheduler |
| filtered_items | UNIQUE(sub_id, item_id) | 预筛丢弃的商品 | scheduler |
| market_price | PK(**platform**, keyword)（v7 起，表重建迁移） | EMA 均价，alpha=0.15，批中位数 | scheduler |
| item_deep_analysis | PK(item_id)（全局，无 sub_id） | 深度分析缓存，6h TTL 语义在 scheduler | scheduler/main |

迁移机制：`PRAGMA user_version` 单调递增块（storage.py:93），加列用 table_info 判存在，加表/重建用 executescript。v7=平台维度。

## LLM 能力来源

插件无自带 LLM client，全部走 `context.llm_generate(chat_provider_id=..., prompt, system_prompt)`：
- `main._make_llm_call`（max_tokens=1200）→ 注入 provider（兜底提取用）
- `main._make_agent_llm_call`（max_tokens=2500）→ 注入 GofishBrowserAgent
- recommender 内部自调
- 约定：`async (prompt, system_prompt) -> str`，失败返回 ""；JSON 鲁棒解析模式见 provider_agent.py:143

## 配置体系（改配置项要同步 4-5 处）

`_conf_schema.json`（AstrBot 面板）→ `app/_admin_schema.json`（Admin WebUI 全集）→
`admin_service.py:_settings_to_editable_values + _config_groups` → `config.py:PluginSettings + load_plugin_settings`。
热更新：Admin 改 → 写 admin_runtime_config.json overlay → POST /api/config/reload → reload_runtime() 重建运行时（DB 连接保留）。**overlay 永远覆盖 AstrBot 面板同名项。**
