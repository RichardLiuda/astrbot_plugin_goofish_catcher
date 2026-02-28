# AstrBot 闲鱼关键词上新与降价监测插件设计深度研究报告

执行摘要（≤200字）：本报告提出一套可落地的 AstrBot 插件方案，用于监测闲鱼特定关键词商品“上新/降价”。公开资料显示闲鱼小程序/合作方能力主要面向定向邀请服务商且需聚石塔，面向全站“关键词搜索+价格追踪”的官方 API 能力未指定；因此推荐以 Playwright 驱动网页搜索并拦截结构化响应作为默认采集方案，配合可配置定时调度、SQLite 价格历史、去重与限速、群/私聊/Webhook 通知与重试机制。同时评估“本地 Playwright 服务 + 远程 AstrBot”模块化部署，并给出 Cloudflare Tunnel 暴露与 Access 认证建议。

## 目标与功能

插件的核心目标是：让用户在 AstrBot 的群聊/私聊中订阅一个或多个关键词，按可配置频率抓取闲鱼搜索结果并检测“上新/降价”，在不刷屏的前提下及时推送提醒，同时具备工程级稳定性（重试、限速、错误隔离、可观测性）。

AstrBot 插件开发规范层面，官方开发指南强调：插件依赖通过 `requirements.txt` 管理、持久化数据应存 `data` 目录、需要良好错误处理避免插件崩溃，并明确不建议使用 `requests` 而建议 `aiohttp/httpx` 等异步库。citeturn0search0turn2view0

功能需求建议拆为“订阅管理、抓取与调度、事件检测、存储与去重、通知、稳定性与运维”六个域：

| 功能域 | 必须支持的功能点 | 关键设计要领 |
|---|---|---|
| 关键词订阅与管理 | 关键词订阅/退订；多关键词管理；按会话（群/私聊）隔离；查询订阅列表；启停单个关键词任务 | 使用 AstrBot 指令/指令组实现交互；会话唯一标识用 `unified_msg_origin` 存储以便后续主动推送。citeturn0search2turn21search1 |
| 定时拉取频率 | 全局默认拉取间隔；每关键词可覆盖；可设置抓取页数/排序方式；错误时退避重试 | WebUI 配置由 `_conf_schema.json` 提供；支持 `template_list` 表达多任务列表；配置会保存到 `data/config/<plugin_name>_config.json`。citeturn23view2turn23view0 |
| 上新判定与降价阈值 | 上新判定规则（首次发现+时间窗口）；降价阈值（绝对/相对）；滑动窗口/历史回溯（可选） | 规则要“抗排序波动/抗重试重复”；降价要加通知冷却时间避免频繁刷屏。 |
| 去重与历史价格存储 | 商品去重；历史价格时间序列；记录已通知事件（NEW/PRICE_DROP） | 默认 SQLite；唯一索引+事件哈希防重；大文件与 DB 放 `data/plugin_data/{plugin_name}/`。citeturn24view1 |
| 通知渠道 | AstrBot 群/私聊主动消息；可扩展 Webhook（HTTP POST） | AstrBot 主动消息：存储 `event.unified_msg_origin`，后续 `self.context.send_message(unified_msg_origin, chains)` 推送。citeturn0search2 |
| 稳定性与限速 | 错误重试（指数退避+抖动）；速率限制处理（并发控制/队列）；失败降级（延后或切换 Provider） | AstrBot 官方开发原则要求“不让插件因一个错误崩溃”；并要求避免使用同步阻塞请求库。citeturn2view0 |

## 技术栈与依赖

### AstrBot 插件框架要点

- 插件通过 `requirements.txt` 管理第三方依赖，是官方推荐的依赖交付方式。citeturn0search0turn2view0  
- 插件配置通过 `_conf_schema.json` 提供 Schema 并在 WebUI 可视化编辑；支持 `template_list` 这种“列表模板”结构，适配“多关键词任务”；并支持 `file` 类型配置项（v4.13.0 之后）用于上传文件。citeturn23view2turn23view0  
- 配置解析后保存到 `data/config/<plugin_name>_config.json`，并在实例化时传入 `AstrBotConfig`。citeturn23view0  
- 插件存储：提供插件级 KV 存储接口（如 `put_kv_data/get_kv_data`），同时要求大文件存放在 `data/plugin_data/{plugin_name}/`。citeturn24view0turn24view1  
- 主动消息：`unified_msg_origin` 是会话唯一 ID，可用于后台任务主动推送。citeturn0search2  

### 推荐依赖清单

| 类别 | 推荐库 | 用途 | 选择理由 |
|---|---|---|---|
| 异步 HTTP 客户端 | `httpx` 或 `aiohttp` | Webhook 通知、远程 Provider 调用、轻量抓取/健康检查 | AstrBot 官方明确不建议 `requests`，建议异步请求库。citeturn2view0 |
| Headless 浏览器 | `playwright` | 渲染闲鱼搜索页、拦截 XHR/Fetch 响应、复用登录态 | Playwright 官方提供认证状态复用（storage state）等机制；适合“少逆向”的采集策略。citeturn10search2 |
| HTML/JSON 解析（可选） | `orjson`/`ujson`、`lxml`/`selectolax` | JSON 快速解析、DOM 备选解析 | DOM 解析作为降级路径；首选网络响应 JSON。 |
| DB（默认） | `sqlite3`（标准库）或 `aiosqlite` | 商品、价格历史、通知记录持久化 | 轻量、单机部署友好；DB 文件按规范放入 `data/plugin_data/{plugin_name}/`。citeturn24view1 |
| DB（可选） | `redis`、`asyncpg` | 多实例共享状态、跨节点去重 | 用户部署平台未指定，作为增强选项。未指定 |
| 调度（可选） | 纯 asyncio 循环 / `APScheduler` | 定时抓取与任务队列 | AstrBot 提供 `on_astrbot_loaded` 钩子，适合启动后台任务；APScheduler 可选但非必需。citeturn21search1 |

### 部署运行环境

- AstrBot 官方支持通过 Docker 部署，并给出端口与数据卷映射示例（`-v $PWD/data:/AstrBot/data`）。citeturn1search3  
- 云函数/Serverless：Playwright 依赖浏览器运行环境，冷启动与资源限制会显著影响稳定性；用户未指定平台，建议优先 Docker/VM。未指定  
- 聚石塔：闲鱼开放平台/合作方服务端接入文档明确提及“服务端通过 code + AppSecret 调用 `taobao.top.auth.token.create` 换 token”，且常见问题明确“小程序后端必须部署聚石塔”。这条路线更偏合作方接入，而非本插件默认部署环境。citeturn3search0turn5view0  

## 数据获取策略

### 官方资料对“全站关键词搜索 API”的可用性判断

从闲鱼官方开放平台“快速接入”文档可见：闲鱼小程序目前“不对外公开开放申请”，只面向“定向邀请的服务商”。citeturn6search1  
同时，开放平台常见问题明确：入驻闲鱼小程序必须部署聚石塔服务，小程序调用的后端接口必须部署到聚石塔。citeturn5view0  

在淘宝开放平台的闲鱼相关 API 中，可见一些“服务商商品查询/卖家发布商品列表”等接口，但它们典型特征是“聚石塔内调用”且（多为）需要授权，例如：  
- `alibaba.idle.isv.item.query`（服务商闲鱼商品查询）：标注“需要授权、聚石塔内调用”，且核心输入是 `item_id`。citeturn8view1  
- `alibaba.idle.item.user.publishitems`（发布的商品列表）：标注“需要授权、聚石塔内调用”，面向“服务商卖家发布商品列表”。citeturn7view0  

这些公开资料并未明确提供“面向全站商品的关键词搜索 + 价格追踪”官方 API 能力，因此本报告对“官方 API 满足本需求”的结论标注为：**未指定**（需要企业资质/对接运营，且 API 能力与范围需进一步确认）。citeturn6search1turn8view1turn7view0  

### 三种采集路线对比（必须表格 + 推荐）

| 路线 | 实现方式 | 优点 | 缺点/风险 | 适配度结论 |
|---|---|---|---|---|
| 官方 API（合作方/TOP/聚石塔） | 走闲鱼开放平台/淘宝开放平台授权与聚石塔调用 | 合规与稳定性最强（若拿到资质） | 小程序仅定向邀请；聚石塔要求明确；公开资料未指定“全站关键词搜索”能力范围 | **企业合作场景优先**；本插件默认不依赖（未指定）citeturn6search1turn5view0 |
| 非官方抓包（MTOP/H5 API） | 直接请求闲鱼网页/客户端调用的接口（需 cookie/签名/风控应对） | 性能高、不需要浏览器渲染 | 协议/签名易变；可能出现“被挤爆/风控/登录跳转”；合规风险更高（非官方） | **可做可插拔 Provider（备选）**；默认不建议深度逆向citeturn3search2turn9search2 |
| 第三方数据服务 | 调用第三方聚合的“闲鱼搜索/监控 API” | 集成快、运维轻 | 数据来源与合法性不透明；成本与 SLA 风险；供应商锁定 | **可做商业版可选**；需法务/合规评估（未指定） |

**首选推荐方案（面向“个人/小团队自部署 AstrBot”）**：  
采用 **Playwright 驱动闲鱼网页搜索 + 拦截网络响应（JSON）** 的方式作为默认 Provider。理由是：与深度逆向相比，Playwright 让网页端自己完成必要的请求构造与执行，插件侧只需要稳定地捕获响应并解析字段；对“接口签名变化”的敏感度更低。同时 Playwright 支持路由拦截与请求中止（可屏蔽图片/字体降低负载）。citeturn11search0turn10search2  

## Playwright 可行性评估

### 能否通过网页查询/搜索

闲鱼存在公开的网页搜索入口（`/search` 页面可访问），因此“从用户视角”具备可自动化的入口。citeturn19search1  
但实际抓取中可能遇到以下情况：  
- 某些接口返回“被挤爆/稍后重试”并给出登录跳转 URL，说明限流与登录态在部分接口上会影响结果可得性。citeturn3search2  

结论：**网页搜索入口可用**，但“是否必须登录、何种频率触发风控”属于运行时变量，需要设计“登录态可选 + 限速 + 退避重试 + 降级”能力。citeturn3search2turn19search1  

### 是否需登录、验证码/滑块与 cookie/session 管理

Playwright 官方文档提供“保存并复用已认证状态（authenticated browser state）”的思路：先产生登录态并保存为文件，后续复用该 state 启动已登录上下文；并建议将保存目录加入 `.gitignore`。citeturn10search2  

非官方社区实现也印证了“登录态/滑块验证”可能是实际门槛：例如非官方 goofish-client 文档描述了 Passport 登录流程、并提到需要有效 Cookie 用于通过滑块验证（该来源为**非官方**，仅用于风险提示）。citeturn6search7  

因此插件应提供三种模式：  
- **匿名模式**：不提供登录态文件；频率更低、页数更少，失败即退避。  
- **登录态模式**：用户上传/配置 Playwright `storage_state` 文件，提升稳定性。citeturn10search2turn23view2  
- **外置浏览器服务模式**：见“模块化部署”章节（本地机器维护登录与浏览器，远端只调 API）。

### 模拟移动端/UA、行为指纹与合规边界

Playwright 可设置 viewport/UA 等浏览器上下文参数，但“验证码/行为指纹/滑块”属于平台风控策略，不可假设一定可绕过。本报告建议策略是：**遇到验证码即降频/暂停并通知用户处理**，而不是实现自动绕过（合规风险高，且维护成本极大）。该部分平台规则细节在公开官方资料中未明确（未指定）。

### 性能与并发限制建议

Playwright 属于重资源组件，建议插件侧强制实施以下资源策略（工程建议）：  
- 全局并发 `max_concurrency=1~2`（单机）；关键词任务串行或小并发队列；  
- `page.route` 层面拦截并中止图片/字体/媒体请求以降低带宽与渲染负担；Playwright Route API 支持 `abort()`/`continue_()` 等处理。citeturn11search0turn11search5  
- 对失败请求指数退避，并引入抖动（jitter）避免“同步重试风暴”；结合站点返回“被挤爆”类错误作熔断。citeturn3search2  

### 具体实现步骤与示例代码片段

**推荐落地步骤**（从“最稳”到“最省事”排序）：

1) 先在人工浏览器中确认搜索结果页可访问，并观察网络请求中是否存在结构化 JSON 响应（通常为 XHR/Fetch）。citeturn19search1  
2) 使用 Playwright 启动浏览器、打开搜索页、监听 `response` 事件并筛选目标 URL（或在 `route` 中捕获特定请求）。citeturn11search0turn11search5  
3) 若匿名模式不稳定，使用 Playwright 认证状态复用：先生成 `storage_state.json`，插件启动时加载该 state。citeturn10search2turn23view2  
4) 将抓取结果标准化为统一字段（`item_id/title/price/publish_time/url`），交由事件检测模块。

**Playwright 示例（简化版，偏伪代码）**：

```python
import asyncio
from urllib.parse import quote
from playwright.async_api import async_playwright

SEARCH_URL = "https://www.goofish.com/search?q={q}"

async def fetch_items(keyword: str, storage_state_path: str | None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx_kwargs = {"viewport": {"width": 1280, "height": 800}}
        if storage_state_path:
            ctx_kwargs["storage_state"] = storage_state_path  # 复用登录状态

        context = await browser.new_context(**ctx_kwargs)

        # 资源降载：屏蔽图片/字体/媒体
        async def route_handler(route):
            if route.request.resource_type in ("image", "font", "media"):
                await route.abort()
            else:
                await route.continue_()
        await context.route("**/*", route_handler)

        page = await context.new_page()

        captured = []

        async def on_response(resp):
            # TODO: 用更精确的 URL/路径匹配避免误捕获
            if "mtop" in resp.url and "search" in resp.url:
                if resp.ok and "application/json" in (resp.headers.get("content-type","")):
                    captured.append(await resp.json())

        page.on("response", on_response)

        await page.goto(SEARCH_URL.format(q=quote(keyword)))
        await page.wait_for_timeout(3000)

        await context.close()
        await browser.close()

        # TODO: parse captured[-1] -> items
        return captured[-1] if captured else None
```

上面展示了 Playwright 的两类关键能力：网络路由控制（`route.abort/continue_`）与认证状态复用（storage state），均为官方文档支持的常见用法。citeturn11search0turn10search2  

## 定时与调度

### 推荐调度模式

AstrBot 提供系统级事件钩子 `@filter.on_astrbot_loaded()`（Bot 初始化完成时触发），非常适合在插件加载后启动后台异步任务。citeturn21search1  
因此，推荐在 `on_astrbot_loaded` 中启动一个“调度 loop”，每 `tick` 扫描到期订阅并投递到队列，队列消费者负责限速与抓取。

可选替代：  
- 外部 cron/调度器：通过 AstrBot HTTP API（v4.18.0 起支持 API Key）触发插件指令或调用自定义接口，但复杂度更高，且需要暴露 HTTP API。citeturn25view0  

### 并发与速率控制策略

- **两级限速**：全局 `Semaphore(max_concurrency)` + 关键词级 `min_interval`；  
- **令牌桶/漏桶（工程建议）**：对“每分钟最大请求数/每分钟最大关键词数”做硬限制；  
- **失败退避**：连续失败提升下一次执行时间（指数退避），并记录失败原因（如登录失效/验证码/被挤爆）。citeturn3search2turn2view0  

### 事件流 mermaid 流程图（定时拉取→数据获取→判定→通知）

```mermaid
flowchart TD
  A[定时调度 tick<br/>扫描到期订阅] --> B[投递抓取任务到队列<br/>按umo+keyword]
  B --> C[限速层<br/>Semaphore + TokenBucket]
  C --> D{Provider选择}
  D -->|Playwright Web搜索| E[拦截响应/解析商品列表]
  D -->|非官方抓包/第三方服务(可选)| E
  E --> F[标准化字段<br/>item_id/title/price/publish_time/url]
  F --> G[事件检测<br/>上新/降价/去重/冷却]
  G --> H[写入存储<br/>items/price_history/notifications]
  H --> I{需要通知?}
  I -->|是| J[构建消息/卡片]
  J --> K[AstrBot主动消息<br/>context.send_message]
  J --> L[可选Webhook POST]
  I -->|否| M[结束等待下一轮]
  K --> M
  L --> M
```

主动消息发送依赖 `unified_msg_origin` 存储并调用 `self.context.send_message`，这是 AstrBot 官方推荐的“定时任务/后台发送”方式。citeturn0search2  

## 事件检测与存储、通知与用户配置

### 事件检测与判定规则（上新/降价/误报控制）

**上新判定（推荐默认）**  
- 主条件：`keyword_id + item_id` 首次出现（数据库不存在）。  
- 时间窗口：若能解析 `publish_time`，要求 `publish_time >= now - new_window`；若无法解析，改用 `first_seen_at` 近似（误差更大）。  
- 排序抖动抑制：同一轮/相邻两轮重复出现的旧 item 不触发通知。

**降价判定（推荐默认）**  
- 对比基准：最近一次观测价 `last_price`（或 lookback 窗口内最高价/中位数，作为可选增强）。  
- 阈值：满足绝对降价 `drop_abs >= abs_threshold` 或相对降幅 `drop_pct >= pct_threshold`。  
- 冷却：同一商品/同一关键词的降价通知至少间隔 `cooldown_sec`，避免频繁小幅波动刷屏。

**伪代码（算法步骤）**：

```text
for sub in due_subscriptions(now):
    items = provider.fetch(sub.keyword, pages=sub.pages)

    for item in items:
        x = normalize(item)  # item_id/title/price/publish_time/url

        if not db.items.exists(sub.id, x.item_id):
            db.items.insert(sub.id, x.item_id, x.title, x.url,
                            first_seen_at=now, publish_time=x.publish_time,
                            last_price=x.price)
            db.price_history.insert(x.item_id, price=x.price, ts=now)

            if within_window(x.publish_time or now, now, sub.new_window_sec) \
               and not db.notifications.exists(sub.id, x.item_id, type="NEW"):
                notify("NEW", sub.umo, x)
                db.notifications.insert(sub.id, x.item_id, "NEW", ts=now)
            continue

        # 已存在：更新 last_seen 与价格序列
        last_price = db.items.get_last_price(sub.id, x.item_id)
        db.items.update_last_seen(sub.id, x.item_id, now)

        if x.price != last_price:
            db.price_history.insert(x.item_id, x.price, ts=now)
            db.items.update_last_price(sub.id, x.item_id, x.price)

        if x.price < last_price:
            drop_abs = last_price - x.price
            drop_pct = drop_abs / last_price

            if (drop_abs >= sub.drop_abs) or (drop_pct >= sub.drop_pct):
                if not db.notifications.rate_limited(sub.id, x.item_id,
                                                     type="PRICE_DROP",
                                                     cooldown=sub.cooldown_sec):
                    notify("PRICE_DROP", sub.umo, x, drop_abs, drop_pct)
                    db.notifications.insert(sub.id, x.item_id, "PRICE_DROP", ts=now,
                                            meta={drop_abs, drop_pct})
```

### 存储与状态管理（数据模型表格：字段与索引）

AstrBot 官方要求大文件存放 `data/plugin_data/{plugin_name}/`，插件可通过工具函数获取该目录；KV 存储适合“小状态”，但价格序列更适合 SQLite。citeturn24view1turn24view0  

**建议 SQLite 表设计**（默认单机；Redis/Postgres 作为可选增强）：

| 表名 | 主要字段（示例） | 约束/索引建议 | 说明 |
|---|---|---|---|
| `subscriptions` | `id`，`umo`，`keyword`，`interval_sec`，`pages`，`drop_abs`，`drop_pct`，`new_window_sec`，`cooldown_sec`，`enabled`，`last_run_at` | `UNIQUE(umo, keyword)`；`INDEX(enabled, last_run_at)` | 会话（群/私聊）级关键词任务 |
| `items` | `id`，`sub_id`，`item_id`，`title`，`url`，`publish_time`(可空)，`first_seen_at`，`last_seen_at`，`last_price` | `UNIQUE(sub_id, item_id)`；`INDEX(sub_id, last_seen_at)`；`INDEX(item_id)` | 每个订阅下的商品快照与最新价 |
| `price_history` | `id`，`item_id`，`price`，`ts`，`source` | `INDEX(item_id, ts DESC)` | 价格时间序列，用于降价/回溯 |
| `notifications` | `id`，`sub_id`，`item_id`，`type`，`sent_at`，`payload_hash` | `INDEX(sub_id, sent_at)`；`UNIQUE(sub_id, item_id, type, payload_hash)` | 去重与审计；payload_hash 允许“同类事件不同内容”策略化去重 |
| `fetch_runs`（可选） | `id`，`sub_id`，`started_at`，`finished_at`，`status`，`err_type`，`err_msg`，`items_count` | `INDEX(sub_id, started_at DESC)` | 可观测性与故障定位 |

### 通知与用户配置（含 _conf_schema.json 草案）

**AstrBot 主动消息**：官方文档建议将 `event.unified_msg_origin` 存储起来，在定时任务或合适时机通过 `self.context.send_message(unified_msg_origin, chains)` 主动推送。citeturn0search2  

**WebUI 配置**：AstrBot 支持 `_conf_schema.json`，并支持 `template_list` 表达多任务列表；配置会保存到 `data/config/<plugin_name>_config.json` 并传入 `AstrBotConfig`。citeturn23view2turn23view0  
此外，`file` 类型 schema（v4.13.0 起）可用于让用户上传 Playwright 登录态文件。citeturn23view2  

下面给出一个“可落地的配置草案”（节选，结构示意）：

```json
{
  "global": {
    "type": "object",
    "description": "全局设置",
    "items": {
      "default_interval_sec": {"type": "int", "default": 600, "description": "默认拉取间隔(秒)"},
      "max_concurrency": {"type": "int", "default": 1, "description": "Playwright全局并发"},
      "max_pages": {"type": "int", "default": 2, "description": "每次最多抓取页数"},
      "login_state_file": {
        "type": "file",
        "description": "Playwright登录态文件(可选)",
        "default": [],
        "file_types": ["json"]
      }
    }
  },
  "subscriptions": {
    "type": "template_list",
    "description": "关键词订阅列表",
    "templates": {
      "watch": {
        "name": "关键词监控",
        "items": {
          "umo": {"type": "string", "description": "目标会话unified_msg_origin"},
          "keyword": {"type": "string", "description": "关键词"},
          "interval_sec": {"type": "int", "default": 600, "description": "拉取间隔(秒)"},
          "drop_abs": {"type": "float", "default": 50, "description": "降价阈值(元)"},
          "drop_pct": {"type": "float", "default": 0.05, "description": "降价阈值(比例0-1)"},
          "new_window_sec": {"type": "int", "default": 1800, "description": "上新窗口(秒)"},
          "cooldown_sec": {"type": "int", "default": 21600, "description": "同商品通知冷却(秒)"},
          "webhook_url": {"type": "string", "default": "", "description": "可选Webhook URL"}
        }
      }
    }
  }
}
```

**示例通知文本**（建议包含关键词、降幅、链接、时间）：

- 上新：
```text
🆕【闲鱼上新】关键词：{keyword}
{title}
价格：¥{price}
时间：{publish_time_or_first_seen}
链接：{url}
```

- 降价：
```text
📉【闲鱼降价】关键词：{keyword}
{title}
现价：¥{price}（上次：¥{last_price}）
降幅：¥{drop_abs}（{drop_pct:.1%}）
链接：{url}
```

## 模块化部署评估：本地 Playwright 服务 + 远程 AstrBot 插件 + Cloudflare Tunnel

这一部分针对你的“额外要求”：Playwright 部署在本地机器（更容易保持登录态、处理验证码/扫码），AstrBot 插件运行在远程服务器（更稳定的 7x24），二者通过安全通道通信。

### 模块化拆分的可行性结论

从工程角度，模块化拆分非常可行，并且能显著改善两类现实问题：  
1) **登录态与风控处理**：本地机器更容易人工介入（扫码/验证码处理），避免在远程服务器上维护图形环境；  
2) **资源与安全边界**：远程 AstrBot 只负责调度、检测、通知与存储；本地服务只负责“抓取执行”，减少远端暴露面。

关键挑战在于：通信安全（认证/加密）、隧道稳定性、任务超时与降级策略。

### 通信协议设计：REST/gRPC/消息队列（推荐 REST）

| 协议 | 适用场景 | 优点 | 缺点 | 推荐度 |
|---|---|---|---|---|
| REST/HTTPS | 单机本地 Node/py 服务，远端插件按需请求 | 实现最简单；调试友好；适合“请求-响应”抓取 | 长任务需处理超时与重试；并发控制要靠服务端 | **高** |
| gRPC | 高吞吐、多语言、强契约 | 流式传输、IDL 规范化强 | 复杂度更高；穿透/网关配置更复杂 | 中 |
| 消息队列（NATS/RabbitMQ/Kafka） | 大规模任务、需要异步回调与可靠投递 | 解耦；天然缓冲；更易做重试/死信队列 | 运维成本高；对个人部署不友好 | 低~中（企业版） |

**推荐：REST/HTTPS**，并在接口层面支持两种调用模式：  
- **同步模式**：适合“抓 1-2 页搜索结果”这种 3~10 秒内的任务；  
- **异步模式（可选）**：远端仅提交任务获取 `job_id`，本地完成后回调远端 webhook 或远端轮询 `/jobs/{id}`。

### 认证与加密：API Key、JWT、mTLS（推荐“隧道 + Access”组合）

**基础层：Cloudflare Tunnel**  
Cloudflare Tunnel 的定位是：无需公网可路由 IP，本地运行的 `cloudflared` 守护进程建立“仅出站（outbound-only）”连接到 Cloudflare 全球网络，从而安全暴露本地资源。citeturn12search0turn12search12  
这解决了“家庭宽带 IP 变化、NAT 穿透、不开入站端口”的问题。

**认证层：Cloudflare Access（强烈建议）**  
Cloudflare 文档说明 Access 可作为应用前的身份认证层。citeturn12search17turn12search13  
对于“远程 AstrBot 插件访问本地抓取服务”这种机器到机器访问，Cloudflare 支持 **Service Token（Client ID + Client Secret）** 用于自动化系统访问受 Access 保护的应用。citeturn12search2  
此外 Access 也涉及基于 JWT 的应用 token 概念（用于理解与扩展鉴权形态）。citeturn12search6  

**应用层补充（可选）**：  
- **API Key（自建）**：在 REST 请求头加 `X-API-Key`（与 AstrBot HTTP API 的 API Key 思路一致，但这是你自建服务的 key）。AstrBot 官方 HTTP API 也采用 API Key（`Authorization: Bearer` 或 `X-API-Key`）的做法，可作为参考范式。citeturn25view0  
- **mTLS**：如果你不通过 Cloudflare Access，而是直接暴露 HTTPS 服务，可考虑 mTLS；但在“已使用 Tunnel + Access”的情况下，mTLS 常常是过度工程（除非高安全要求）。

### Cloudflare Tunnel 暴露到公网的安全性与可用性评估

**隧道工作方式与端口要求**  
- Tunnel 是“出站连接”，cloudflared 连接 Cloudflare 全球网络。citeturn12search0turn12search12  
- 防火墙需要允许 cloudflared 出站连接到 Cloudflare（文档给出端口 7844，协议可为 QUIC/HTTP2，对应 UDP/TCP）。citeturn12search4turn12search12  

**快速暴露与生产建议**  
- 开发预览可用 `cloudflared tunnel --url http://localhost:<port>` 快速启动，并输出一个可访问的 tunnel URL。citeturn12search1  
- 也可使用 Quick Tunnels（trycloudflare）生成随机子域名并代理到 localhost（更偏临时）。citeturn12search19  
生产环境更建议使用“本地管理/命名 tunnel + 固定域名 + Access 策略”，避免随机 URL 带来的变更与管控困难（此为工程建议；官方文档对 quick tunnel 的描述强调其随机性）。citeturn12search19turn12search5  

**健康检查、断线恢复与可观测性**  
Cloudflare 提供 tunnel health check 概念，用于探测 Cloudflare 能否通过 tunnel 访问某个指定端点。citeturn12search3  
另外 Cloudflare 文档也提到可在配置层做“连接冗余、自动 failover、负载均衡”等优化（适合多连接或多实例 cloudflared）。citeturn12search8  

> 带宽/延迟：Cloudflare 文档未给出面向你这个场景的明确 SLA 数字（未指定）。工程上应通过压测确定“每轮抓取耗时”和“最大安全并发”，并把这些参数暴露在配置里。

### 性能与可靠性：延迟影响、并发限制、降级策略

**延迟影响**：  
- 对“搜索抓取”这种 IO 密集任务，网络延迟会直接影响单轮任务耗时；如果你把 Playwright 执行从远端搬到本地，再通过 Cloudflare Tunnel 访问，本质上是“远端→Cloudflare→本地”的额外一跳。  
- 但相比在远端直接跑 Playwright 的收益是：本地更容易维持登录态与人工干预，整体成功率往往更高（经验判断，官方资料未指定）。

**并发限制建议（模块化场景）**：  
- 远端插件侧：对本地服务调用做 `Semaphore`，例如全局最多 1~2 个并发请求；  
- 本地抓取服务侧：严格限制浏览器实例数与页面数（例如 1 个浏览器 + 1~2 个 context），超出则排队；并暴露 `/metrics` 或至少 `/health` 来告知队列长度。

**故障降级策略（必须覆盖）**：  
- 本地服务不可用：远端插件进入“降级模式”  
  - 方案 A：延后重试（指数退避），不做轻量抓取（最安全）；  
  - 方案 B：使用轻量 HTTP 抓取/第三方服务（若已配置），但要明确这是不同风险等级的数据源（未指定）；  
- 登录失效/验证码：本地服务返回结构化错误码（如 `AUTH_REQUIRED`/`CAPTCHA`），远端插件暂停该订阅并通知管理员处理。

### 运维建议：本地资源规划、日志采集、密钥管理、监控告警

**本地机器资源规划（建议值，需压测校准）**：  
- CPU：≥ 2 核（并发 1 的 Playwright）；并发 2 建议 4 核；  
- 内存：≥ 2~4GB（1 浏览器实例）；并发/多上下文会显著上升；  
- 磁盘：至少数百 MB 用于浏览器/缓存/日志；登录态文件与截图（如开启）也占用空间。  
上述为工程经验建议，官方资料未指定。

**证书与密钥管理**：  
- Cloudflare Access 的 Service Token（Client ID/Secret）应作为机密存储在远端 AstrBot 的环境变量或密钥管理服务中，不写入仓库。citeturn12search2  
- 本地服务如果再加自定义 API Key，同样应通过环境变量注入。

**日志与远程采集**：  
- 本地服务：记录每次任务耗时、失败原因（被挤爆/登录跳转/解析失败）、队列长度；  
- 远端插件：记录每个订阅的“拉取成功率、通知数量、连续失败次数”；AstrBot 官方强调良好错误处理与测试。citeturn2view0  
- 告警：当连续 N 次 `AUTH_REQUIRED` 或 `CAPTCHA`，自动在管理员会话推送告警。

### 示例实现：简洁 REST API 规范 + 伪代码

#### REST API 规范示例（建议 v1）

**认证建议**：优先 Cloudflare Access（Service Token）保护入口；应用层再加 `X-API-Key` 双保险（工程建议）。citeturn12search2turn12search17  

**接口列表**：

1) `GET /health`  
- 用途：健康检查、版本与队列状态  
- 响应示例：
```json
{
  "status": "ok",
  "version": "1.0.0",
  "queue_depth": 2,
  "browser_slots": {"max": 1, "in_use": 1}
}
```

2) `POST /v1/search`（同步模式）  
- 请求 JSON（示例）：
```json
{
  "keyword": "显卡 4070",
  "pages": 2,
  "sort": "time_desc",
  "use_login": true,
  "timeout_ms": 15000
}
```
- 响应 JSON（示例）：
```json
{
  "ok": true,
  "items": [
    {
      "item_id": "1234567890",
      "title": "RTX 4070 99新",
      "price": 3699.0,
      "publish_time": "2026-02-28T10:20:00+08:00",
      "url": "https://www.goofish.com/item?id=1234567890"
    }
  ],
  "meta": {"provider": "playwright", "elapsed_ms": 4200}
}
```

3) 统一错误响应：
```json
{
  "ok": false,
  "error": {
    "code": "AUTH_REQUIRED | CAPTCHA | RATE_LIMITED | TIMEOUT | PARSE_ERROR",
    "message": "human readable",
    "retry_after_sec": 300
  }
}
```

#### Playwright 服务端伪代码（接收任务→执行→返回）

```text
start server
init global semaphore(max_browser=1)
load storage_state from local disk (optional)

POST /v1/search:
  verify auth (Access headers / API key)
  validate input (keyword length, pages range)
  acquire semaphore with timeout
  try:
      run playwright:
          new_context(storage_state, viewport)
          route abort images/fonts/media
          goto search url
          collect json responses that match pattern
          parse to normalized items
      return ok + items
  except captcha/auth redirect:
      return error code CAPTCHA/AUTH_REQUIRED
  except timeout:
      return TIMEOUT with retry_after
  finally:
      release semaphore
```

#### AstrBot 插件端伪代码（远端 Provider 调用、超时/重试、入库与通知）

```text
on_astrbot_loaded:
  create background poll_loop()

poll_loop():
  every tick:
    due = select subscriptions where now-last_run >= interval
    for sub in due:
       enqueue(sub)

worker():
  while true:
    sub = dequeue()
    resp = call local_service /v1/search with timeout=xx
    if resp.ok:
        normalized_items = resp.items
        detect_events_and_persist(sub, normalized_items)
        send_notifications_via_astrbot(sub.umo)
    else:
        if resp.error.code in (AUTH_REQUIRED, CAPTCHA):
            pause subscription and notify admin
        else:
            schedule retry with exponential backoff
```

其中 `on_astrbot_loaded` 钩子与主动推送能力是 AstrBot 官方文档给出的标准用法：初始化完成后启动后台任务；并用 `unified_msg_origin` 进行会话定位发送。citeturn21search1turn0search2  

## 反爬与合规性、测试监控与部署、工时与里程碑

### 反爬与合规性注意事项

1) **优先尊重官方开放能力边界**：闲鱼开放平台明确“小程序不对外公开开放申请，仅定向邀请服务商”，并要求聚石塔；这意味着普通开发者很难通过官方渠道获得“全站关键词搜索”能力，任何非官方抓取都要更谨慎。citeturn6search1turn5view0  
2) **频率控制与限流风险**：官方服务端接入文档提示“避免同一用户每次进入都重新获取 code，否则可能会被限流”，从侧面说明限流真实存在。citeturn3search0  
3) **robots.txt 可用性**：本次公开资料检索未能直接核验 goofish.com 的 robots.txt 规则（未指定）。你仍应把 robots.txt 视为“减少站点负担的约定机制”；Google 文档也说明 robots.txt 主要用于避免站点收到过多请求，并不是强制访问控制。citeturn14search4  
4) **不做验证码/滑块自动绕过**：如果出现账号限制或验证码，应降频并提示用户人工处理；这是降低封禁风险与合规风险的关键工程策略（实现细节未指定）。  
5) **最小化采集与存储**：仅保存商品 ID、标题、价格、链接、时间戳与必要的去重字段；避免采集聊天内容、个人隐私信息等。

### 测试、监控与部署

**测试要点**：AstrBot 官方开发原则要求“功能需经过测试、良好注释、良好错误处理、提交前用 ruff 格式化”，并强调持久化数据放 `data` 目录。citeturn2view0  
建议最低测试集：  
- 单元测试：事件检测（新发现、降价阈值、冷却时间、去重 hash）  
- 集成测试：SQLite 迁移与索引、Provider 输出字段契约  
- 端到端测试（可选）：Playwright 在稳定网络下的“最小抓取”回归（不建议在 CI 中高频跑）

**监控指标（建议）**：  
- 抓取成功率、平均耗时、解析失败率、连续失败次数  
- 错误分类统计（AUTH_REQUIRED/CAPTCHA/RATE_LIMITED/TIMEOUT）——可参考真实接口返回“被挤爆/稍后重试”这一类错误表现。citeturn3search2  
- 通知量与去重命中率（防刷屏）

**部署步骤（Docker）**：AstrBot 官方提供 Docker 部署方式与数据卷映射到 `/AstrBot/data` 的示例。citeturn1search3  

**示例 Dockerfile（包含 Playwright 安装注意事项）**：
```dockerfile
FROM soulter/astrbot:latest

# 插件依赖建议写入插件 requirements.txt，AstrBot会按插件安装；此处为镜像级可复现示例
RUN pip install --no-cache-dir playwright httpx aiosqlite

# 安装浏览器与系统依赖（Playwright官方推荐方式之一）
RUN python -m playwright install --with-deps chromium

# 数据目录通过运行时 volume 挂载：-v $PWD/data:/AstrBot/data（见官方部署文档）
```
运行与端口/数据卷映射可直接参考 AstrBot 官方 Docker 部署文档。citeturn1search3  

### 开发时间估算与里程碑（粗略）

结合 AstrBot 插件机制与 Playwright 工程不确定性（登录态、限流、解析结构变动），建议以“先可用后稳定”的节奏推进：

| 里程碑 | 交付范围 | 优先级 | 粗略工时 |
|---|---|---|---|
| MVP | 指令订阅/列表/退订；on_astrbot_loaded 启动后台任务；Playwright 抓 1 页；上新通知；SQLite 入库 | P0 | 3–5 天 |
| 降价与去重增强 | 价格历史表；降价阈值（绝对/相对）；冷却时间；通知记录表；失败退避 | P0 | 3–5 天 |
| WebUI 配置完善 | `_conf_schema.json`：template_list、多任务编辑、file 上传登录态；配置热更新 | P1 | 1–2 天 citeturn23view2turn2view0 |
| 模块化部署增强 | 本地 Playwright 服务 REST；远端插件 Provider；Cloudflare Tunnel + Access（Service Token）接入；健康检查与降级 | P1 | 3–6 天 citeturn12search0turn12search2 |
| 测试与运维 | pytest/ruff；日志指标与告警；Docker/文档 | P1 | 2–4 天 citeturn2view0turn1search3 |

> 注：如果你决定走“非官方抓包 + 签名逆向”路线，工期与维护成本会显著上升，且合规风险更高（不建议作为默认实现；该能力在公开官方资料中未指定）。