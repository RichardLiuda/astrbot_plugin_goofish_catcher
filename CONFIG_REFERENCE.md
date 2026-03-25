# 配置参考

这份文档补充 README 中没有展开的配置项说明，适合在已经跑通插件之后按需微调。

## 模式选择

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `provider_mode` | `playwright_local` | 本地浏览器模式；如需把浏览器放到远端 worker，改为 `remote_rest` |

## 本地 Playwright

| 配置项 | 默认值 | 建议 |
| --- | --- | --- |
| `playwright_storage_state_file` | `[]` | 本地登录态文件路径，建议指向固定的 `storage_state.json` |
| `playwright_executable_path` | `""` | 想用系统 Chrome/Chromium 时再填，建议绝对路径 |
| `playwright_block_assets` | `true` | 建议保持开启，减少图片/字体加载 |
| `playwright_force_direct` | `true` | 建议保持开启，减少系统代理造成的 IP 波动 |

## 远程 Worker

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `remote_base_url` | `""` | 远端 worker 的 HTTPS 地址，不要带结尾斜杠 |
| `remote_headers` | `[]` | 额外请求头列表；Cloudflare Access 常用 `CF-Access-Client-Id` 和 `CF-Access-Client-Secret` |
| `remote_api_key` | `""` | 如果 worker 走 API Key 鉴权就填；走 Cloudflare Access 时留空 |
| `remote_timeout_sec` | `20` | 远端接口默认超时，慢机器可以调到 `30-45` |
| `remote_healthcheck_on_init` | `true` | 建议开启，插件启动时先探测远端 `/health` |
| `remote_healthcheck_timeout_sec` | `10` | 远端健康检查超时 |

## 调度与抓取

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `default_interval_sec` | `600` | 新建订阅时的默认轮询间隔 |
| `default_pages` | `1` | 新建订阅与查询默认抓取页数 |
| `max_pages` | `2` | 抓取页数上限；建议保持 `1-2` |
| `scheduler_tick_sec` | `15` | 调度器扫描到期订阅的间隔 |
| `max_concurrency` | `1` | 并发 worker 数；闲鱼场景强烈建议先保持 `1` |
| `queue_max_size` | `256` | 任务队列上限 |
| `fetch_timeout_sec` | `20` | 单次抓取超时；慢机器可调到 `30-45` |
| `max_retries` | `3` | 普通失败时的自动重试次数 |
| `retry_base_sec` | `30` | 第一次退避等待时间 |
| `retry_max_sec` | `900` | 最大退避时间 |

补充说明：

- 2.0.0 遇到 `CAPTCHA` 会先重试 2 次，再进入补登录态流程。
- 外层总超时已经按重试总时长放大，不需要为了三次重试额外手算总预算。

## 事件阈值

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `default_new_window_sec` | `1800` | 上新判定时间窗 |
| `default_drop_abs` | `50.0` | 绝对降价阈值，单位元 |
| `default_drop_pct` | `0.05` | 相对降价阈值，`0.05 = 5%` |
| `default_cooldown_sec` | `21600` | 同类通知冷却时间 |

## LLM 相关

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `llm_enabled` | `true` | 是否启用 LLM 推荐 |
| `llm_provider_id` | `""` | 推荐分析模型 |
| `llm_prefilter_provider_id` | `""` | 初筛模型 |
| `llm_timeout_sec` | `25` | 推荐阶段超时 |
| `llm_top_k` | `3` | 返回推荐数量 |
| `llm_min_score` | `0.0` | 最低推荐分，低于该值的结果不输出 |
| `llm_max_candidates` | `20` | 参与推荐的最大候选数 |
| `llm_prefilter_enabled` | `true` | 是否启用 LLM 初筛 |
| `llm_prefilter_timeout_sec` | `6` | 初筛超时 |
| `llm_prefilter_max_items` | `30` | 初筛最大输入商品数 |

如果你只是想先跑起来：

- 可以先保持 `llm_enabled = true`
- `llm_provider_id` 留空，先用默认可用模型
- 如果模型不稳定，插件会自动回退到启发式逻辑

## 通知与 WebUI

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `webhook_url` | `""` | 额外 Webhook 通知地址，不需要时留空 |
| `admin_webui_enabled` | `false` | 是否启用内置管理后台 |
| `admin_webui_host` | `127.0.0.1` | WebUI 监听地址 |
| `admin_webui_port` | `8790` | WebUI 监听端口 |
| `admin_webui_api_key` | `""` | WebUI API Key |

## 常见推荐取值

### 保守稳定型

- `provider_mode = playwright_local`
- `default_interval_sec = 600`
- `default_pages = 1`
- `max_pages = 1`
- `max_concurrency = 1`
- `fetch_timeout_sec = 20`
- `playwright_force_direct = true`

### 远程 worker 常用型

- `provider_mode = remote_rest`
- `remote_healthcheck_on_init = true`
- `remote_timeout_sec = 20-30`
- worker 侧 `fetch_timeout_sec = 20-30`
- worker 侧 `max_pages = 1-2`
- worker 侧 `force_direct = true`

## 补登录态相关说明

- 本地模式下，建议直接运行 `save_state.py` 更新 `storage_state.json`
- 远程模式下，推荐使用 2.0.0 的自动补登录态流程
- 如果远程 worker 返回 `CAPTCHA`，插件会自动重试 2 次
- 重试后仍失败时，会向首次触发的会话发送二维码截图
- 扫码后在同一会话回复任意消息即可继续

## 还想看什么

- 远程部署、Tunnel、Access 细节：看 [REMOTE_SETUP.md](./REMOTE_SETUP.md)
- 快速入门、命令、排查：看 [README.md](./README.md)
