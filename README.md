# astrbot_plugin_goofish_catcher

AstrBot 闲鱼关键词监控插件（命令优先，双阶段架构）。

## 功能

- 关键词订阅/退订/列表/暂停/恢复
- 后台定时抓取（`on_astrbot_loaded` 启动）
- 原始结果相关性预筛选（优先 LLM，失败回退本地关键词匹配）
- 上新检测 + 降价检测（含去重与冷却）
- SQLite 持久化（订阅、商品、价格历史、通知、抓取记录）
- 支持主动消息通知（`unified_msg_origin`）和可选 Webhook
- `立即检查` 返回 LLM TopK 投资建议（失败自动回退启发式评分）
- `查询` 支持免订阅抓取并返回 LLM 推荐结果
- 定时任务仅在本轮有候选事件时发送一条 TopK 摘要
- `明细` 命令读取最近一次缓存结果，不重复抓取

## 命令

- `/闲鱼 订阅 <关键词> [interval_sec] [pages]`
- `/闲鱼 退订 <关键词>`
- `/闲鱼 列表`
- `/闲鱼 暂停 <关键词>`
- `/闲鱼 恢复 <关键词>`
- `/闲鱼 立即检查 [关键词]`
- `/闲鱼 查询 <关键词...> [--pages N]`
- `/闲鱼 明细 <关键词> [limit]`
- `/闲鱼 状态`

## 安装

1. 安装依赖：
   - `aiosqlite`
   - `httpx`
   - `playwright`
2. 首次运行前安装浏览器：
   - `uv run python -m playwright install chromium chromium-headless-shell`

## 配置项（`_conf_schema.json`）

核心抓取与调度：

- `default_interval_sec`, `default_pages`, `max_pages`
- `scheduler_tick_sec`, `max_concurrency`, `queue_max_size`
- `fetch_timeout_sec`, `retry_base_sec`, `retry_max_sec`
- `default_new_window_sec`, `default_drop_abs`, `default_drop_pct`, `default_cooldown_sec`
- `playwright_storage_state_file`
- `playwright_block_assets`
- `webhook_url`

LLM 建议相关：

- `llm_enabled`
- `llm_provider_id`（WebUI 下拉选择 AstrBot 已配置模型）
- `llm_timeout_sec`
- `llm_top_k`
- `llm_max_candidates`

原始结果预筛选（快速）：

- `llm_prefilter_enabled`
- `llm_prefilter_timeout_sec`
- `llm_prefilter_max_items`

## 行为说明

- 抓取后先做“相关性预筛选”（只看关键词匹配，不看价格与功能），再进入上新/降价检测。
- 定时监控：仅当本轮检测到上新/降价候选时，才触发 LLM（或回退评分）并发送一条摘要。
- 立即检查：抓取后直接返回 TopK 建议。
- 查询命令：无需订阅，支持空格关键词（整段文本作为关键词）；可用 `--pages N` 或 `-p N` 指定抓取页数。
- 明细命令：读取最近一次缓存快照（来自定时拉取或立即检查），不触发新抓取。
- 如未配置可用模型或模型超时，自动降级到本地启发式逻辑，不中断抓取。
- 当前版本固定使用本地 Playwright Provider，并强制有头模式；远程 Provider 配置将在后续版本恢复。

## 风险说明

- 页面结构变化可能导致解析失败（`PARSE_ERROR`）。
- 登录态失效或验证码触发会暂停订阅并告警（不做自动绕过）。
- 建议保持低并发，结合退避策略，避免触发风控。
