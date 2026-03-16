# astrbot_plugin_goofish_catcher

闲鱼关键词监控插件（命令优先）。  
支持订阅轮询、上新/降价检测、LLM 推荐分析、免订阅临时查询。 
提供webui管理，理论上可以脱离astrbot聊天平台工作（）

目前很多功能都比较原始，可能配置起来会有点麻烦，请见谅！

由于需要用到`playwright`的有头浏览器，对机器配置有一定要求，如果在服务器上运行，建议至少2G2C起步，否则可能会出现问题。

针对服务器性能不够的问题，鼠鼠已经实现将`playwright`模块化并远程部署到本地机器的feature。具体请参考[REMOTE_SETUP.md](./REMOTE_SETUP.md)。

- 里面有涉及到Cloudflare Zero Trust的相关配置，用于内网穿透，如果有公网ip就不需要配置（不过既然都有公网ip的服务器能跑playright的话，感觉也不需要用到这个功能吧）
- 如果有不懂的地方或者表达不清晰之处，可以先尝试问ai，或者直接提交issue，鼠鼠看到会第一时间帮助解答的喵

如果有大佬能贡献一下pr的话，感激不尽！

如果觉得插件有帮助，欢迎star！Ciallo～(∠・ω< )⌒★

## 环境要求

| 依赖         | 建议版本    | 说明                   |
| ---------- | ------- | -------------------- |
| Python     | >= 3.10 | 与 AstrBot 运行环境一致     |
| AstrBot    | >= 4.x  | 需要指令系统 + Provider 能力 |
| Playwright | 最新稳定版   | 用于闲鱼页面抓取             |

## 版本进度（TODO）

### 已实现

- 本地 Playwright Provider 抓取链路（P0）
- 远程 Provider（P1）可用链路（`remote_rest`）
- 远程健康检查与统一错误码对接（`/health`、`/v1/search`）
- Cloudflare Tunnel + Access / API Key 接入配置
- 命令优先交互：订阅/退订/列表/暂停/恢复/立即检查/查询/明细/状态
- 相关性初筛（LLM 优先，失败回退规则）
- LLM 推荐 TopK（失败自动回退启发式）
- SQLite 持久化与定时调度
- 查询命令支持空格关键词与 `--pages/-p` 参数
- WebUI 配置项支持推荐模型与初筛模型下拉选择

### 当前无法实现

- 经检验当前无法稳定支持 **无头模式抓取闲鱼**，因此本版本强制使用有头浏览器。
- 当前不实现 **验证码自动绕过**（仅检测并暂停订阅，需人工处理登录/风控）。

## 功能概览

- 关键词订阅/退订/列表/暂停/恢复
- 后台定时抓取（`on_astrbot_loaded` 自动启动调度）
- 原始结果相关性初筛（优先 LLM，失败回退关键词规则）
- 上新检测 + 降价检测（去重 + 冷却）
- LLM TopK 推荐（不可用时自动回退启发式打分）
- 免订阅即时查询（`/闲鱼 查询`）
- SQLite 持久化（订阅、商品快照、价格历史、通知、抓取记录）
- 主动消息通知 + 可选 Webhook

## 安装与启动

1. 安装依赖

```bash
uv pip install -r data/plugins/astrbot_plugin_goofish_catcher/requirements.txt
```

2. 安装 Playwright 浏览器

```bash
uv run python -m playwright install chromium chromium-headless-shell
```

3. 启动 AstrBot，插件会自动加载

如果你希望本地模式改用系统 Chrome/Chromium，可在插件配置里填写 `playwright_executable_path`。

## 远程 Worker（`remote_rest`）

远程模式下，AstrBot 插件只负责调度与通知，浏览器、登录态和抓取都放在远端 worker 上。

链路如下：

`AstrBot 插件 -> RemoteSearchProvider(httpx) -> Cloudflare Tunnel/HTTPS -> worker_server.py -> PlaywrightSearchProvider -> 闲鱼`

### 1. 远端机器准备登录态

远端 worker 所在机器执行一次手动登录：

```powershell
uv run python .\save_state.py
```

如果已经配置了 `worker_config.json` 里的 `executable_path`，或者设置了 `GOOFISH_WORKER_EXECUTABLE_PATH`，`save_state.py` 会优先使用同一个浏览器路径。

建议把生成的 `storage_state.json` 放到单独目录，例如：

```powershell
New-Item -ItemType Directory -Force .\worker_data | Out-Null
Move-Item .\storage_state.json .\worker_data\storage_state.json -Force
```

### 2. 启动远端 worker

最推荐的方式是放一个本地 `worker_config.json`，后续只维护这一个文件。

示例：

```json
{
  "data_dir": "./worker_data",
  "storage_state_file": "./worker_data/storage_state.json",
  "executable_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "cf_access_client_id": "<your-cf-client-id>",
  "cf_access_client_secret": "<your-cf-client-secret>",
  "max_pages": 2,
  "fetch_timeout_sec": 20,
  "block_assets": true,
  "force_direct": true
}
```

然后直接启动：

```powershell
uv run python -m uvicorn worker_server:app --host 127.0.0.1 --port 8787
```

如果你想把配置文件放到别的位置，可以指定：

```powershell
$env:GOOFISH_WORKER_CONFIG = "D:\path\to\worker_config.json"
uv run python -m uvicorn worker_server:app --host 127.0.0.1 --port 8787
```

仍然支持环境变量方式；环境变量优先级高于 JSON 配置。老的环境变量启动方式如下：

```powershell
$env:GOOFISH_WORKER_DATA_DIR = ".\worker_data"
$env:GOOFISH_WORKER_STORAGE_STATE_FILE = "storage_state.json"
$env:GOOFISH_WORKER_EXECUTABLE_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
$env:GOOFISH_WORKER_CF_ACCESS_CLIENT_ID = "<your-cf-client-id>"
$env:GOOFISH_WORKER_CF_ACCESS_CLIENT_SECRET = "<your-cf-client-secret>"
uv run python -m uvicorn worker_server:app --host 127.0.0.1 --port 8787
```

如果你不用 Cloudflare Access，也可以只配置 API Key：

```powershell
$env:GOOFISH_WORKER_API_KEY = "<your-api-key>"
uv run python -m uvicorn worker_server:app --host 127.0.0.1 --port 8787
```

### 3. 用 Cloudflare Tunnel 暴露 worker

将本地 `127.0.0.1:8787` 暴露成 HTTPS 域名，例如：

- `https://goofish-worker.example.com`

推荐在 Tunnel 前挂 Cloudflare Access service token，不要直接把 worker 裸暴露到公网。

### 4. AstrBot WebUI 配置示例

如果走 Cloudflare Access：

- `provider_mode`: `remote_rest`
- `remote_base_url`: `https://goofish-worker.example.com`
- `remote_timeout_sec`: `20`
- `remote_healthcheck_on_init`: `true`
- `remote_headers`:

```text
CF-Access-Client-Id: <your-cf-client-id>
CF-Access-Client-Secret: <your-cf-client-secret>
```

如果走 API Key：

- `provider_mode`: `remote_rest`
- `remote_base_url`: `https://goofish-worker.example.com`
- `remote_api_key`: `<your-api-key>`
- `remote_headers`: 留空

### 5. 健康检查与状态

- 插件初始化时会按 `remote_healthcheck_on_init` 先请求远端 `/health`
- `/闲鱼 状态` 会额外显示远程地址、最近一次健康检查时间和远程健康详情
- 远端 `/health` 会返回当前鉴权状态以及 `storage_state.json` 是否存在

### 6. 远程错误语义

- worker 返回 `AUTH_REQUIRED / CAPTCHA / RATE_LIMITED / TIMEOUT / PARSE_ERROR` 时，插件仍沿用现有暂停/退避逻辑
- worker 自身鉴权失败或网络异常，会映射为 `NETWORK_ERROR`，不会误判成闲鱼登录态问题

### 7. Cloudflare Tunnel 返回 502 的一次典型原因

如果同时满足下面几个现象：

- worker 主机本机访问 `http://127.0.0.1:8787/health` 正常，能返回 JSON
- AstrBot 宿主机或其他外部机器访问 `https://<your-domain>/health` 时返回 `502`
- `cloudflared` debug 日志里反复出现 `timeout: no recent network activity`、`failed to dial a quic connection`

那么问题大概率不在插件、不在 `CF-Access-Client-Id / Secret`，而是在 `cloudflared` 默认使用的 QUIC/UDP 链路不稳定。表现上会像“worker 本机偶尔可用，其他机器持续 502”，或者不同地区/不同时间返回结果不一致。

这种情况下，建议先强制把 tunnel 协议切到 HTTP/2：

```bash
cloudflared tunnel run --protocol http2 --token <your-tunnel-token>
```

如果恢复正常，再把常驻启动方式也改成 `--protocol http2`。另外建议顺手升级 `cloudflared`：

```bash
brew update
brew upgrade cloudflared
```

这个场景下，`502` 的根因通常是 Tunnel 到 Cloudflare Edge 的 QUIC 连接频繁断开，而不是 worker 应用本身故障。

## 登录态准备（建议）

闲鱼对未登录/风控会比较敏感，建议先准备 `storage_state.json` 并在 WebUI 配置 `playwright_storage_state_file`。

### Windows（PowerShell）

1. 进入插件目录，直接运行仓库内脚本并手动登录

```powershell
uv run python .\save_state.py
```

如果 worker 侧已经配置 `executable_path` / `GOOFISH_WORKER_EXECUTABLE_PATH`，这个脚本也会优先使用相同浏览器。

2. 移动到插件数据目录（可选但推荐）

```powershell
New-Item -ItemType Directory -Force .\data\plugin_data\astrbot_plugin_goofish_catcher | Out-Null
Move-Item .\storage_state.json .\data\plugin_data\astrbot_plugin_goofish_catcher\storage_state.json -Force
```

### macOS / Linux（Bash）

1. 进入插件目录，直接运行仓库内脚本并手动登录

```bash
uv run python ./save_state.py
```

如果 worker 侧已经配置 `executable_path` / `GOOFISH_WORKER_EXECUTABLE_PATH`，这个脚本也会优先使用相同浏览器。

2. 移动到插件数据目录（可选但推荐）

```bash
mkdir -p ./data/plugin_data/astrbot_plugin_goofish_catcher
mv ./storage_state.json ./data/plugin_data/astrbot_plugin_goofish_catcher/storage_state.json
```

### 如需改用系统 Chrome / Chromium

在 WebUI 中额外设置 `playwright_executable_path`，建议填写绝对路径。

- Windows 示例：`C:\Program Files\Google\Chrome\Application\chrome.exe`
- macOS 示例：`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- Linux 示例：`/usr/bin/google-chrome`

如果显式配置了这个路径，但路径不存在或浏览器启动失败，插件会直接报错，不会静默回退到 Playwright 自带 Chromium。

### 在 WebUI 中生效

1. 打开插件配置，设置 `playwright_storage_state_file` 指向 `storage_state.json`
2. 保存配置并重载插件
3. 如订阅已被暂停，执行：

```text
/闲鱼 恢复 <关键词>
```

## 指令说明（AstrBot 行为）

| 指令                                    | 作用      | 行为说明                                       |
| ------------------------------------- | ------- | ------------------------------------------ |
| `/闲鱼 订阅 <关键词> [interval_sec] [pages]` | 新建/更新订阅 | 保存订阅后会自动触发一次检查入队                           |
| `/闲鱼 退订 <关键词>`                        | 删除订阅    | 仅删除当前会话该关键词订阅                              |
| `/闲鱼 列表`                              | 查看订阅    | 显示启用/暂停状态、页数、下次执行时间                        |
| `/闲鱼 暂停 <关键词>`                        | 暂停订阅    | 暂停后不再参与定时轮询                                |
| `/闲鱼 恢复 <关键词>`                        | 恢复订阅    | 恢复后会立即触发一次检查入队                             |
| `/闲鱼 立即检查 [关键词]`                      | 订阅检查    | 传关键词：同步执行该订阅并返回推荐；不传：批量入队当前会话所有启用订阅        |
| `/闲鱼 查询 <关键词...> [--pages N]`         | 免订阅查询   | 直接抓取并返回推荐；支持空格关键词，末尾可用 `--pages`/`-p` 指定页数 |
| `/闲鱼 明细 <关键词> [limit]`                | 查看缓存明细  | 读取该订阅最近一次缓存快照，不重新抓取                        |
| `/闲鱼 状态`                              | 运行状态    | 查看调度器、队列、Provider、DB 与当前会话订阅概况             |

## 关键行为规则

### 1) 定时轮询

- 调度器按 `scheduler_tick_sec` 扫描到期订阅并入队。
- 仅在本轮出现候选事件（上新/降价）时发送摘要通知，避免刷屏。

### 2) 推荐与初筛

- 抓取后先做相关性初筛（只判断“是否像目标商品”）。
- 初筛通过后再做推荐评分（LLM 或启发式回退）。
- LLM 不可用、超时或输出异常时，不中断主流程。

### 3) 查询 vs 立即检查

- `查询`：不依赖订阅，不写订阅状态，适合临时看盘。
- `立即检查`：面向已订阅关键词，会更新订阅运行数据与缓存。

### 4) 明细来源

- `明细` 只读最近一次缓存（来自定时轮询或立即检查）。
- `明细` 不触发新抓取，因此响应更快且稳定。

## 配置项（`_conf_schema.json`）

### 抓取与调度

| 配置项                    | 说明            | 默认值   |
| ---------------------- | ------------- | ----- |
| `default_interval_sec` | 默认轮询间隔（秒）     | `600` |
| `default_pages`        | 默认抓取页数        | `1`   |
| `max_pages`            | 最大抓取页数        | `2`   |
| `scheduler_tick_sec`   | 调度扫描间隔（秒）     | `15`  |
| `max_concurrency`      | 最大并发 Worker 数 | `1`   |
| `queue_max_size`       | 任务队列最大长度      | `256` |
| `fetch_timeout_sec`    | 单次抓取超时（秒）     | `20`  |
| `max_retries`          | 最大重试次数        | `3`   |
| `retry_base_sec`       | 重试基础退避（秒）     | `30`  |
| `retry_max_sec`        | 重试最大退避（秒）     | `900` |

### 事件阈值

| 配置项                      | 说明          | 默认值     |
| ------------------------ | ----------- | ------- |
| `default_new_window_sec` | 上新判定窗口（秒）   | `1800`  |
| `default_drop_abs`       | 绝对降价阈值（元）   | `50.0`  |
| `default_drop_pct`       | 相对降价阈值（0-1） | `0.05`  |
| `default_cooldown_sec`   | 同类通知冷却（秒）   | `21600` |

### Playwright 与通知

| 配置项                             | 说明            | 默认值    |
| ------------------------------- | ------------- | ------ |
| `provider_mode`                 | 抓取模式，支持本地或远程  | `"playwright_local"` |
| `playwright_storage_state_file` | 登录态 JSON 文件   | `[]`   |
| `playwright_executable_path`    | 本地浏览器可执行文件路径 | `""`   |
| `playwright_block_assets`       | 是否拦截图片/字体/媒体  | `true` |
| `playwright_force_direct`       | 是否强制直连禁用代理    | `true` |
| `webhook_url`                   | 可选 Webhook 地址 | `""`   |

### 远程 Provider

| 配置项                           | 说明                                      | 默认值    |
| ----------------------------- | --------------------------------------- | ------ |
| `remote_base_url`             | 远程 worker 的基础地址                          | `""`   |
| `remote_api_key`              | 远程 worker API Key                       | `""`   |
| `remote_headers`             | 远程请求附加 Header 列表，每行 `Header: Value`      | `[]`   |
| `remote_timeout_sec`          | 远程请求默认超时（秒）                             | `20`   |
| `remote_healthcheck_on_init`  | 初始化时是否先探测远程 `/health`                   | `true` |
| `remote_healthcheck_timeout_sec` | 初始化远程健康检查超时（秒）                       | `10`   |

### LLM 推荐

| 配置项                         | 说明             | 默认值    |
| --------------------------- | -------------- | ------ |
| `llm_enabled`               | 是否启用 LLM 推荐    | `true` |
| `llm_provider_id`           | 推荐模型（WebUI 下拉） | `""`   |
| `llm_prefilter_provider_id` | 初筛模型（WebUI 下拉） | `""`   |
| `llm_timeout_sec`           | 推荐分析超时（秒）      | `25`   |
| `llm_top_k`                 | 推荐返回数量         | `3`    |
| `llm_max_candidates`        | 参与推荐的最大候选数     | `20`   |
| `llm_prefilter_enabled`     | 是否启用 LLM 初筛    | `true` |
| `llm_prefilter_timeout_sec` | 初筛超时（秒）        | `6`    |
| `llm_prefilter_max_items`   | 初筛最大商品数        | `30`   |

## 数据落盘位置

- 插件数据目录：`data/plugin_data/astrbot_plugin_goofish_catcher`
- SQLite 文件：`goofish_catcher.db`

主要表：

- `subscriptions`
- `items`
- `price_history`
- `notifications`
- `fetch_runs`

## 常见问题排查

### 1) AUTH_REQUIRED / CAPTCHA

现象：

- 日志出现 `paused due to AUTH_REQUIRED` 或 `CAPTCHA`

处理：

1. 检查 `playwright_storage_state_file` 是否存在且有效。
2. 用有头浏览器重新登录并更新 `storage_state.json`。
3. 执行 `/闲鱼 恢复 <关键词>` 恢复任务。

### 2) 抓取商品数为 0

处理：

1. 确认闲鱼页面实际可见商品。
2. 降低并发、增加超时、保持有头模式。
3. 检查 `playwright_force_direct` 是否为 `true`（避免系统代理切换 IP）。
4. 检查关键词是否过窄，或被初筛过滤。

### 3) 查询关键词被截断

请使用：

- `/闲鱼 查询 适马 60-600 Sports`
- `/闲鱼 查询 适马 60-600 Sports -p 2`

说明：`查询` 支持空格关键词，整段文本会作为关键词解析。

有其他问题欢迎提交issue！

## 风险与建议

- 闲鱼页面结构变化可能导致 `PARSE_ERROR`。
- 高频抓取可能触发风控，建议低并发 + 合理间隔。
- 本插件没做验证码绕过。
  - 欢迎大佬狠狠用pr灌注鼠鼠（欧尼该）

