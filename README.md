<div align="center">

![:name](https://count.getloli.com/@goofish_catcher?name=goofish_catcher&theme=minecraft&padding=6&offset=0&align=top&scale=1&pixelated=1&darkmode=auto)

# 闲鱼蹲蹲助手

_✨ 闲鱼关键词监控与商品好价推荐推送 ✨_

[![License](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot 4.x+](https://img.shields.io/badge/AstrBot-4.x%2B-orange.svg)](https://github.com/Soulter/AstrBot)
[![GitHub](https://img.shields.io/badge/作者-RichardLiu-blue)](https://github.com/RichardLiuda)

</div>

<div align="center">
<br>

# 🤖 **v3.0.0 全面 Agent 化** 🤖

直接对 LLM 说"帮我搜二手镜头"、"给键盘订个降价提醒"——自动调工具、驱动真实浏览器、进度实时推流到对话，即问即用。

<br>
</div>

> [!CAUTION]
> **远程模式用户请务必同步更新 Worker 代码。** v3.0.0 新增了 Agent 远程执行接口，旧版 Worker 与新版插件不兼容。

> 最近鼠鼠比较忙，有issue或者任何疑问都可以用邮箱联系喵：2645345468@qq.com

本插件的开发缘由：某人在闲鱼蹲一颗镜头蹲了三个月，期间被卖家跑单三次，觉得还是自己手速不够快，遂诞生了这个插件。目前已经帮某人蹲到了几个好价商品，这玩意还是挺有用的（）

如果觉得插件有帮助，欢迎star！Ciallo～(∠・ω< )⌒★

## 环境要求

| 场景 | 最低建议 | 说明 |
| --- | --- | --- |
| Python | `>= 3.10` | 与 AstrBot 运行环境保持一致 |
| AstrBot | `>= 4.x` | 需要命令系统、Provider 与插件配置能力 |
| 本地模式 | 建议 `2C2G` 起步 | Chromium 有头浏览器运行在 AstrBot 同机 |
| 远程模式 | AstrBot 宿主机要求较低，Worker 建议 `2C2G` 起步 | 浏览器负载主要落在远端 Worker |

补充说明：

- 远程模式下，本地插件进程**不需要** Playwright；只有 Worker 机器需要安装浏览器。
- 不提供验证码自动绕过；当前方案是"检测到 CAPTCHA 或登录态失效后自动拉起补登录态流程，由你扫码继续"。

## v3.0.0 核心能力

- 支持本地模式 `playwright_local` 与远程模式 `remote_rest`
- 支持订阅、退订、暂停、恢复、立即检查、查询、明细、状态
- 支持后台轮询、上新检测、降价检测、去重通知
- 支持 LLM 初筛与推荐，失败时自动回退启发式逻辑
- 支持为单条订阅设置"推荐最高价"阈值，超过阈值的商品不会进入最终推荐
- 支持对推荐消息直接"引用回复序号收藏"，可回复 `1`、`1 3`、`1,2`
- 支持统一补登录态：二维码截图下发、扫码后回复任意消息继续、扫码成功自动点击「快速进入」、自动恢复暂停订阅
- 支持 WebUI 管理与运行状态查看
- **浏览器 Agent**：LLM 可调用 `goofish_browser_task` 驱动真实 Chromium 执行复杂页面任务；进度实时推流到对话界面；远程模式下 Agent 运行在 Worker，本地无需 Playwright
- **`goofish_search_live` 搜索工具**：LLM 可调用的快速脚本化搜索，支持引用回复序号收藏，适合日常询价场景
- **aiocqhttp 合并转发**：使用 aiocqhttp 渠道时，商品列表以合并转发消息发出，防止刷屏；引用转发消息回复仍可触发收藏
- **订阅操作二次确认**：LLM 在创建、删除、修改订阅前会先向用户确认，避免误操作

## 先看哪份文档

- 想快速跑起来：继续看本 README
- 想做完整远程部署：看 [REMOTE_SETUP.md](./REMOTE_SETUP.md)
- 想查所有配置项含义：看 [CONFIG_REFERENCE.md](./CONFIG_REFERENCE.md)

## 快速开始

### 1. 安装依赖

```bash
uv pip install -r data/plugins/astrbot_plugin_goofish_catcher/requirements.txt
uv run python -m playwright install chromium chromium-headless-shell
```

> 如果使用远程模式，本地可跳过 playwright install，只在 Worker 机器上安装即可。

### 2. 选择部署方式

- 只有一台机器、资源够用：用 `playwright_local`
- AstrBot 跑在服务器、服务器资源紧张，或你想把浏览器放到本地电脑：用 `remote_rest`

### 3. 本地模式最小步骤

1. 在插件配置里保持 `provider_mode = playwright_local`
2. 保存并重载插件
3. 直接发送一次 `/闲鱼 登录`，按提示扫码完成登录
4. 使用 `/闲鱼 订阅 <关键词>` 或 `/闲鱼 查询 <关键词>` 开始使用，或者直接向 LLM 说"帮我搜一下……"

如启用了淘宝（`taobao_enabled = true`，仅本地模式支持），发送 `/闲鱼 登录 淘宝` 用手机淘宝 App 扫码登录；淘宝登录态独立保存（`storage_state.taobao.json`），与闲鱼互不影响。

如果你想改用系统 Chrome/Chromium，再额外填写 `playwright_executable_path`。

### 4. 远程模式最小步骤

1. 在远端 Worker 机器准备 `worker_config.json`
2. 启动 Worker：

```bash
uv run python -m uvicorn worker_server:app --host 127.0.0.1 --port 8787
```

3. 用 Tunnel、反向代理或公网 HTTPS 暴露 Worker
4. 在 AstrBot WebUI 中设置：
   - `provider_mode = remote_rest`
   - `remote_base_url = https://your-worker.example.com`
   - 如需 Cloudflare Access 认证，填写 `CF-Access-Client-Id` 与 `CF-Access-Client-Secret`；其他 Header 填写 `remote_headers_json`
5. 保存并重载插件

远端 `worker_config.json` 最小示例：

```json
{
  "data_dir": "./worker_data",
  "storage_state_file": "storage_state.json",
  "fetch_timeout_sec": 20,
  "max_pages": 2,
  "block_assets": true,
  "force_direct": true
}
```

如果你需要 Cloudflare Access、Tunnel、Worker 环境变量优先级等完整说明，直接看 [REMOTE_SETUP.md](./REMOTE_SETUP.md)。

## 浏览器 Agent

`goofish_browser_task` 是暴露给 LLM 的工具，让大模型可以驱动一个真实 Chromium 完成无法用固定脚本搞定的任务，比如收藏商品、查看卖家在售列表、判断商品图片瑕疵、多步页面交互等。Agent 执行进度会实时推流到对话界面，LLM 可根据执行结果继续推理。

> **定位说明**：`goofish_browser_task` 是"兜底"工具，用于不规则或复杂的页面任务。日常搜索查询请优先使用更快的 `goofish_search_live`。

### 启用条件

- 插件配置中 `llm_agent_enabled = true`（默认开启）
- AstrBot 中已配置好可用的 LLM Provider

### 本地模式 Agent

无需额外配置，满足启用条件即可。Agent 会在插件进程内启动独立 Chromium，登录态自动从本地 `storage_state.json` 继承。

可选调整（WebUI 或 `admin_runtime_config.json`）：

| 配置项 | 说明 | 默认 |
| --- | --- | --- |
| `llm_agent_headless` | `false` = 显示浏览器窗口，便于本地调试 | `false` |
| `llm_agent_max_concurrent` | 同时运行的最大 Agent 数；每个 Agent 独占一个 Chromium 进程 | `3` |
| `llm_agent_step_timeout_sec` | 每步 LLM 推理的最大等待时间（秒） | `60` |
| `llm_agent_provider_id` | 指定用于 Agent 推理的 Provider；留空时回退到推荐分析模型 | 空 |

### 远程模式 Agent

远程模式下，Agent 的 Chromium 运行在 Worker 机器上，插件本地不需要 Playwright。Worker 需要额外配置一个 OpenAI 兼容的 LLM API：

在 `worker_config.json` 中添加：

```json
{
  "llm_api_key": "sk-...",
  "llm_base_url": "https://api.openai.com/v1",
  "llm_model": "gpt-4o-mini",
  "llm_step_timeout_sec": 60,
  "agent_enabled": true,
  "agent_headless": true,
  "agent_max_concurrent": 3
}
```

也可以用环境变量覆盖：

| 环境变量 | 对应字段 | 说明 |
| --- | --- | --- |
| `GOOFISH_WORKER_LLM_API_KEY` | `llm_api_key` | 必填；留空则 Worker 侧 Agent 不启用 |
| `GOOFISH_WORKER_LLM_BASE_URL` | `llm_base_url` | 默认 `https://api.openai.com/v1` |
| `GOOFISH_WORKER_LLM_MODEL` | `llm_model` | 默认 `gpt-4o-mini` |
| `GOOFISH_WORKER_LLM_STEP_TIMEOUT_SEC` | `llm_step_timeout_sec` | 默认 `60` |
| `GOOFISH_WORKER_AGENT_ENABLED` | `agent_enabled` | 默认 `true` |
| `GOOFISH_WORKER_AGENT_HEADLESS` | `agent_headless` | 默认 `true` |
| `GOOFISH_WORKER_AGENT_MAX_CONCURRENT` | `agent_max_concurrent` | 默认 `3` |

> **注意**：Worker 的 LLM 与 AstrBot 侧的 LLM Provider 完全独立。Worker 直接调用 OpenAI 兼容 API，不经过 AstrBot。

## 统一补登录态流程

`playwright_local` 和 `remote_rest` 都使用同一套对话内补登录态流程。

### 自动流程

1. 插件检测到 `CAPTCHA` 时，会先自动重试 2 次
2. 如果仍然是 `CAPTCHA`，就进入补登录态流程
3. 插件会拉起登录窗口，并把当前登录页截图发回 AstrBot 对话
4. 你直接在对话里扫码登录
5. 扫码完成后，插件自动点击「快速进入」按钮，完成认证恢复
6. 在同一会话回复任意消息即可继续
7. 插件会自动保存登录态、恢复相关订阅，并继续执行队列

### 手动控制

- `/闲鱼 登录`：手动拉起登录流程；如果流程已经存在，会给 owner 会话刷新截图
- `/闲鱼 登录取消`：取消当前登录恢复流程

说明：

- 队列在补登录态期间会暂停等待，不会继续乱跑任务。
- `登录完成` 不是必须指令；回复任意普通消息就可以继续。
- 登录成功后，插件会优先接管当前扫码成功的活跃浏览器会话，而不是立刻关闭后重开。
- 如果你更习惯 CLI，也可以运行 `save_state.py` 手动更新本地 `plugin_data/storage_state.json`。

## 推荐消息回复收藏

- 对带有"引用本消息回复序号可收藏"提示的推荐消息，可以直接引用并回复序号完成收藏。
- 支持格式：`1`、`1 3`、`1,2`、`1、2`
- **aiocqhttp 渠道**：商品列表以合并转发消息发出，引用转发消息并回复序号同样可以触发收藏（无需引用具体单条）。
- 如果收藏时检测到登录态失效或验证码，插件会自动转入补登录态流程。

## 常用指令

| 指令 | 作用 |
| --- | --- |
| `/闲鱼 订阅 <关键词> [interval_sec] [pages]` | 创建或更新订阅，并自动入队一次检查 |
| `/闲鱼 退订 <关键词>` | 删除当前会话对应关键词订阅 |
| `/闲鱼 列表` | 查看当前会话全部订阅 |
| `/闲鱼 暂停 <关键词>` | 暂停某个订阅 |
| `/闲鱼 恢复 <关键词>` | 恢复订阅并立即重新入队 |
| `/闲鱼 立即检查 [关键词]` | 对单个订阅同步检查；不带关键词时批量检查当前会话全部启用订阅 |
| `/闲鱼 查询 <关键词...> [--pages N]` | 不建订阅，直接抓取并返回推荐 |
| `/闲鱼 明细 <关键词> [limit]` | 查看最近一次缓存快照 |
| `/闲鱼 状态` | 查看调度器、Provider、队列、远端健康状态 |
| `/闲鱼 登录` | 手动触发补登录态 |
| `/闲鱼 登录取消` | 取消当前补登录态 |

补充：

- 收藏不需要额外命令。对支持收藏的推荐消息直接"引用 + 回复序号"即可。
- LLM 对话中可以直接说"帮我搜一下……"或"给 XX 订阅降价提醒"，插件会自动调用对应工具；创建/删除/修改订阅时，LLM 会先向你确认。

## 运行规则

### 调度与通知

- 调度器会按 `scheduler_tick_sec` 扫描到期订阅并入队。
- 只有出现上新、降价等候选事件时才会推送通知。
- 同类通知受冷却时间控制，避免刷屏。

### 查询、立即检查、定时轮询的区别

- `查询`：临时看盘，不依赖订阅，不更新订阅状态。
- `立即检查`：针对已有订阅，更新订阅运行信息与缓存。
- 定时轮询：后台自动执行，命中事件时主动通知。

### 超时与重试

- 遇到 `CAPTCHA` 时，抓取会先重试 2 次。
- 外层总超时已经按重试总时长展开，不会在第 1 次或第 2 次还没结束时被本地提前截断。
- 普通失败会按退避策略重试；登录态类问题会转入补登录态流程。

## 数据与配置放哪

- 插件数据目录：`data/plugin_data/astrbot_plugin_goofish_catcher`
- SQLite：`goofish_catcher.db`
- 本地登录态：插件自动维护在 `plugin_data/storage_state.json`
- 远端登录态：Worker 自己的 `storage_state_file`

详细配置项、默认值、推荐取值已经拆到 [CONFIG_REFERENCE.md](./CONFIG_REFERENCE.md)。

## 常见问题排查

### 1. 已经弹出登录窗，但 AstrBot 侧还是超时

优先检查：

- `fetch_timeout_sec` 是否过小
- 远端 Worker 主机是否太慢，导致单次页面加载本身就接近超时

当前版本已经做了两层处理：

- `CAPTCHA` 先重试 2 次
- 总超时按重试总时长展开

如果仍然频繁超时，建议先把 `fetch_timeout_sec` 提高到 `30-45`，并保持 `max_pages = 1-2`、`max_concurrency = 1`。

### 2. 出现 `AUTH_REQUIRED` 或 `CAPTCHA`

- 本地模式：可直接发送 `/闲鱼 登录`，或重新运行 `save_state.py` 更新本地稳定登录态文件后执行 `/闲鱼 恢复 <关键词>`
- 远程模式：正常情况下会自动进入补登录态流程；如果没有触发，可手动发送 `/闲鱼 登录`
- 如果是引用回复收藏过程中触发，也会自动进入同一套补登录态流程。

### 3. 远端模式收不到二维码截图

优先检查：

- `/闲鱼 状态` 中远端健康检查是否正常
- `remote_base_url` 是否可访问
- 认证 Header（`CF-Access-Client-Id` / `CF-Access-Client-Secret` 或 `remote_api_key`）是否配置正确
- Worker 机器是否真的能拉起有头浏览器

### 4. 抓取结果一直为 0

常见原因：

- 关键词本身结果就很少
- 页面被风控、未完全加载或被重定向
- 初筛把不相关结果过滤掉了
- 并发过高、页数过多、代理导致 IP 不稳定

建议先把：

- `max_concurrency` 设为 `1`
- `max_pages` 设为 `1-2`
- `playwright_force_direct` 保持 `true`

### 5. Cloudflare Tunnel 访问 Worker 返回 502

如果本机访问 `http://127.0.0.1:8787/health` 正常，但外部访问 HTTPS 域名是 `502`，常见原因是 `cloudflared` 的 QUIC/UDP 链路不稳定。优先尝试：

```bash
cloudflared tunnel run --protocol http2 --token <your-tunnel-token>
```

更完整的远程排查步骤见 [REMOTE_SETUP.md](./REMOTE_SETUP.md)。

### 6. remote 模式登录确认时报 `502` / 网关错误

如果 AstrBot 侧提示远端登录确认接口返回 HTML 或网关错误，通常说明请求还没进入 Worker 的 FastAPI 逻辑，而是先被反向代理或隧道层拦截了。优先检查：

- 反向代理是否把 `/v1/auth/confirm`、`/v1/favorite` 等 POST 请求正确转发到 Worker
- Cloudflare Tunnel / Nginx / 反代是否对长连接或请求体有额外限制
- Worker 机器上是否真的有对应的 `worker auth confirm` 日志

如果 Worker 侧完全没有收到请求，问题通常不在插件，而在代理层。

### 7. 查询关键词被空格截断

请直接把整段关键词写在命令后面，例如：

```text
/闲鱼 查询 神牛 v850 二代
/闲鱼 查询 适马 60-600 Sports -p 2
```

有其他问题欢迎提交 issue！

## 风险与建议

- 闲鱼页面结构变化可能导致 `PARSE_ERROR`（v3.0.0 起 Agent 降级兜底覆盖了更多此类情况）。
- 高频抓取可能触发风控，建议低并发 + 合理间隔。
- 本插件没做验证码绕过。
  - 欢迎大佬狠狠用pr灌注鼠鼠（欧尼该）
