<div align="center">

![:name](https://count.getloli.com/@goofish_catcher?name=goofish_catcher&theme=minecraft&padding=7&offset=0&align=top&scale=1&pixelated=1&darkmode=auto)

# 闲鱼蹲蹲助手

_✨ 闲鱼关键词监控与远端补登录态 ✨_

[![License](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot 4.x+](https://img.shields.io/badge/AstrBot-4.x%2B-orange.svg)](https://github.com/Soulter/AstrBot)
[![GitHub](https://img.shields.io/badge/作者-RichardLiu-blue)](https://github.com/RichardLiuda)

</div>

本插件的开发缘由：某人在闲鱼蹲一颗镜头蹲了三个月，期间被卖家跑单三次，觉得还是自己手速不够快，遂诞生了这个插件。目前已经帮某人蹲到了几个好价商品，这玩意还是挺有用的（）  
支持订阅轮询、上新/降价检测、LLM 推荐分析、免订阅临时查询。  
提供webui管理，理论上可以脱离astrbot聊天平台工作。

目前很多功能都比较原始，可能配置起来会有点麻烦，请见谅！

由于需要用到`playwright`的有头浏览器，对机器配置有一定要求，如果在服务器上运行，建议至少2G2C起步，否则可能会出现问题。

针对服务器性能不够的问题，鼠鼠已经实现将`playwright`模块化并远程部署到本地机器的feature。具体请参考[REMOTE_SETUP.md](./REMOTE_SETUP.md)。

- 里面有涉及到Cloudflare Zero Trust的相关配置，用于内网穿透，如果有公网ip就不需要配置（不过既然都有公网ip的服务器能跑playright的话，感觉也不需要用到这个功能吧）
- 如果有不懂的地方或者表达不清晰之处，可以先尝试问ai，或者直接提交issue，鼠鼠看到会第一时间帮助解答的喵

如果有大佬能贡献一下pr的话，感激不尽！

如果觉得插件有帮助，欢迎star！Ciallo～(∠・ω< )⌒★

## 环境要求

| 场景 | 最低建议 | 说明 |
| --- | --- | --- |
| Python | `>= 3.10` | 与 AstrBot 运行环境保持一致 |
| AstrBot | `>= 4.x` | 需要命令系统、Provider 与插件配置能力 |
| 远程模式 | AstrBot 宿主机要求较低，Worker 建议 `2C2G` 起步 | 浏览器负载主要落在远端 worker |

补充说明：

- 当前仍然强制使用有头浏览器，不支持稳定的无头抓取。
- 不提供验证码自动绕过；2.0.0 的方案是“检测 CAPTCHA 后自动拉起补登录态流程，由你扫码继续”。

## 2.0.0 当前能力

- 支持本地模式 `playwright_local`
- 支持远程模式 `remote_rest`
- 支持订阅、退订、暂停、恢复、立即检查、查询、明细、状态
- 支持后台轮询、上新检测、降价检测、去重通知
- 支持 LLM 初筛与推荐，失败时自动回退启发式逻辑
- 支持远端 worker 健康检查与统一错误码
- 支持远端登录恢复：二维码截图下发、扫码后回复任意消息继续、自动恢复暂停订阅
- 支持 WebUI 管理与运行状态查看

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

### 2. 选择部署方式

- 只有一台机器、资源够用：用 `playwright_local`
- AstrBot 跑在服务器、服务器资源紧张，或你想把浏览器放到本地电脑：用 `remote_rest`

### 3. 本地模式最小步骤

1. 在插件配置里保持 `provider_mode = playwright_local`
2. 运行一次登录态脚本：

```bash
uv run python ./save_state.py
```

3. 在 WebUI 中设置 `playwright_storage_state_file`
4. 保存并重载插件
5. 使用 `/闲鱼 订阅 <关键词>` 或 `/闲鱼 查询 <关键词>` 开始使用

如果你想改用系统 Chrome/Chromium，再额外填写 `playwright_executable_path`。

### 4. 远程模式最小步骤

1. 在远端 worker 机器准备 `worker_config.json`
2. 启动 worker：

```bash
uv run python -m uvicorn worker_server:app --host 127.0.0.1 --port 8787
```

3. 用 Tunnel、反向代理或公网 HTTPS 暴露 worker
4. 在 AstrBot WebUI 中设置：
   - `provider_mode = remote_rest`
   - `remote_base_url = https://your-worker.example.com`
   - `remote_api_key` 或 `remote_headers`
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

如果你需要 Cloudflare Access、Tunnel、worker 环境变量优先级等完整说明，直接看 [REMOTE_SETUP.md](./REMOTE_SETUP.md)。

## 远端补登录态流程

这是 2.0.0 最重要的变化之一，针对 `remote_rest` 生效。

### 自动流程

1. 插件检测到 `CAPTCHA` 时，会先自动重试 2 次
2. 如果仍然是 `CAPTCHA`，就进入补登录态流程
3. 远端 worker 会拉起登录窗口，并把当前登录页截图发回 AstrBot 对话
4. 你直接在对话里扫码登录
5. 扫码完成后，在同一会话回复任意消息即可继续
6. 插件会自动保存远端登录态、恢复相关订阅，并继续执行队列

### 手动控制

- `/闲鱼 登录`
  - 手动拉起远端登录流程
  - 如果流程已经存在，会给 owner 会话刷新截图
- `/闲鱼 登录取消`
  - 取消当前远端登录恢复流程

说明：

- 队列在补登录态期间会暂停等待，不会继续乱跑任务。
- `登录完成` 现在不是必须指令；回复任意普通消息就可以继续。
- 如果是本地模式，仍然建议直接重新运行 `save_state.py`。

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
| `/闲鱼 登录` | 手动触发远端补登录态 |
| `/闲鱼 登录取消` | 取消当前远端补登录态 |

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
- 本地登录态：你在 WebUI 里填写的 `playwright_storage_state_file`
- 远端登录态：worker 自己的 `storage_state_file`

详细配置项、默认值、推荐取值已经拆到 [CONFIG_REFERENCE.md](./CONFIG_REFERENCE.md)。

## 常见问题排查

### 1. 已经弹出登录窗，但 AstrBot 侧还是超时

优先检查：

- 你是否已经升级到 2.0.0
- `fetch_timeout_sec` 是否过小
- 远端 worker 主机是否太慢，导致单次页面加载本身就接近超时

2.0.0 已经做了两层处理：

- `CAPTCHA` 先重试 2 次
- 总超时按重试总时长展开

如果仍然频繁超时，建议先把 `fetch_timeout_sec` 提高到 `30-45`，并保持 `max_pages = 1-2`、`max_concurrency = 1`。

### 2. 出现 `AUTH_REQUIRED` 或 `CAPTCHA`

- 本地模式：重新运行 `save_state.py`，更新登录态文件后执行 `/闲鱼 恢复 <关键词>`
- 远程模式：正常情况下会自动进入补登录态流程；如果没有触发，可手动发送 `/闲鱼 登录`

### 3. 远端模式收不到二维码截图

优先检查：

- `/闲鱼 状态` 中远端健康检查是否正常
- `remote_base_url` 是否可访问
- `remote_api_key` / `remote_headers` 是否配置正确
- worker 机器是否真的能拉起有头浏览器

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

### 5. Cloudflare Tunnel 访问 worker 返回 502

如果本机访问 `http://127.0.0.1:8787/health` 正常，但外部访问 HTTPS 域名是 `502`，常见原因是 `cloudflared` 的 QUIC/UDP 链路不稳定。优先尝试：

```bash
cloudflared tunnel run --protocol http2 --token <your-tunnel-token>
```

更完整的远程排查步骤见 [REMOTE_SETUP.md](./REMOTE_SETUP.md)。

### 6. 查询关键词被空格截断

请直接把整段关键词写在命令后面，例如：

```text
/闲鱼 查询 神牛 v850 二代
/闲鱼 查询 适马 60-600 Sports -p 2
```

有其他问题欢迎提交 issue！

## 风险与建议

- 闲鱼页面结构变化可能导致 `PARSE_ERROR`。
- 高频抓取可能触发风控，建议低并发 + 合理间隔。
- 本插件没做验证码绕过。
  - 欢迎大佬狠狠用pr灌注鼠鼠（欧尼该）
