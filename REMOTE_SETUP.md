# 远程 Worker 部署与配置说明

本文档总结 `astrbot_plugin_goofish_catcher` 远程模式 `remote_rest` 的完整落地流程，覆盖：

- 远程主机准备
- `worker_server.py` 启动
- Cloudflare Tunnel 配置
- Cloudflare Access Service Token 配置
- AstrBot 插件配置
- 联调验证
- 常见问题排查

适用架构：

`AstrBot 插件 -> RemoteSearchProvider -> Cloudflare Access + Tunnel -> worker_server.py -> PlaywrightSearchProvider -> 闲鱼`

## 一、最终推荐方案

推荐采用下面这套组合：

- 远程主机运行 `worker_server.py`
- 远程主机本地监听 `127.0.0.1:8787`
- Cloudflare Tunnel 暴露 `https://worker.example.com`
- Cloudflare Access 使用 `Service Auth + Service Token`
- AstrBot 通过 `remote_headers` 列表传递 `CF-Access-Client-Id` 和 `CF-Access-Client-Secret`
- worker 自身不再做第二层 API Key / CF Token 校验

原因：

- Cloudflare Access 已经是外层门禁
- worker 再用同一套 Cloudflare 头做二次鉴权，会造成重复校验和 401
- 生产上更简单，也更不容易配错

## 二、远程主机准备

远程主机至少需要：

- 当前插件目录
- Python 运行环境
- `requirements.txt` 依赖
- Playwright 浏览器

安装依赖：

```bash
uv pip install -r requirements.txt
uv run python -m playwright install chromium chromium-headless-shell
```

## 三、生成登录态

在远程主机项目目录执行：

```bash
mkdir -p ./worker_data
uv run python save_state.py
mv ./storage_state.json ./worker_data/storage_state.json
```

执行 `save_state.py` 后会打开浏览器，需要在远程主机手动登录闲鱼。

登录态最终建议放在：

```text
./worker_data/storage_state.json
```

## 四、配置 `worker_config.json`

推荐在远程主机项目根目录放一个本地配置文件：

```json
{
  "data_dir": "./worker_data",
  "storage_state_file": "storage_state.json",
  "max_pages": 2,
  "fetch_timeout_sec": 20,
  "block_assets": true,
  "force_direct": true
}
```

注意：

- `storage_state_file` 推荐写成 `storage_state.json`
- 不要写成 `./worker_data/storage_state.json`
- 因为 `data_dir` 已经是 `./worker_data`，如果再带前缀，会被重复拼接

如果一定要写完整路径，请写绝对路径，例如：

```json
{
  "data_dir": "./worker_data",
  "storage_state_file": "/Users/yourname/Documents/Code/astrbot_plugin_goofish_catcher/worker_data/storage_state.json"
}
```

## 五、启动远程 Worker

如果 `worker_config.json` 在项目根目录，直接启动：

```bash
uv run python -m uvicorn worker_server:app --host 127.0.0.1 --port 8787
```

如果配置文件不在当前目录，显式指定：

```bash
export GOOFISH_WORKER_CONFIG="/absolute/path/to/worker_config.json"
uv run python -m uvicorn worker_server:app --host 127.0.0.1 --port 8787
```

如果之前设置过旧环境变量，建议先清掉，避免覆盖 JSON：

```bash
unset GOOFISH_WORKER_API_KEY
unset GOOFISH_WORKER_CF_ACCESS_CLIENT_ID
unset GOOFISH_WORKER_CF_ACCESS_CLIENT_SECRET
unset GOOFISH_WORKER_CONFIG
```

然后重新设置 `GOOFISH_WORKER_CONFIG` 并启动。

## 六、验证本地 Worker 是否正常

先在远程主机本机验证：

```bash
curl http://127.0.0.1:8787/health
```

正确情况下应返回：

```json
{"ok":true,"provider":"playwright_local","auth":"disabled","storage_state":true}
```

这里最关键的是：

- `ok: true`
- `storage_state: true`

其中：

- `auth: disabled` 是正常的，因为推荐只让 Cloudflare Access 做外层鉴权

## 七、配置 Cloudflare Tunnel

### 1. 远程主机安装并登录 `cloudflared`

macOS：

```bash
brew install cloudflared
cloudflared tunnel login
```

### 2. 创建 Tunnel

```bash
cloudflared tunnel create goofish-worker
cloudflared tunnel route dns goofish-worker worker.example.com
```

### 3. 配置入口

如果采用本地配置文件方式，最终 tunnel 应指向：

```text
http://127.0.0.1:8787
```

在 Cloudflare Dashboard 的 Tunnel Route 页面填写：

- Hostname: `worker.example.com`
- Path: 留空
- Service Type: `HTTP`
- URL: `127.0.0.1:8787`

不要填 path，例如 `/blog`；因为 worker 需要同时处理：

- `/health`
- `/v1/search`

### 4. 启动 Tunnel

```bash
cloudflared tunnel run goofish-worker
```

## 八、配置 Cloudflare Access

### 1. 创建 Service Token

路径：

- `Cloudflare Zero Trust`
- `Access`
- `Service Auth`
- `Service Tokens`
- `Create service token`

创建后会得到：

- `Client ID`
- `Client Secret`

注意：

- `Client Secret` 只显示一次
- 泄露后必须重建 token

### 2. 创建 Self-hosted Access 应用

应用域名填：

```text
worker.example.com
```

### 3. 策略必须使用 `Service Auth`

正确策略：

- Policy Action: `Service Auth`
- Include: `Service Token = 你创建的 token 名称`

错误配置示例：

- `ALLOW + Service Token`
- `ALLOW + Everyone`
- 同时混用浏览器登录策略导致跳转登录页

如果配置正确，带 `CF-Access-Client-Id/Secret` 请求时不会再返回 302 登录跳转。

## 九、从本地验证 Cloudflare 外网访问

Windows / PowerShell：

```powershell
curl.exe -i --max-time 30 "https://worker.example.com/health" -H "CF-Access-Client-Id: YOUR_CLIENT_ID" -H "CF-Access-Client-Secret: YOUR_CLIENT_SECRET"
```

正确返回：

```json
{"ok":true,"provider":"playwright_local","auth":"disabled","storage_state":true}
```

如果返回：

- `302 Found`
  说明 Access 策略还在走登录流程，通常是策略类型不是 `Service Auth`
- `401 Unauthorized` 且 body 为 `worker authorization failed`
  说明 worker 自己还在做二次鉴权，需删掉 worker 本地 API Key / CF Token 配置
- `storage_state: false`
  说明远程主机登录态文件路径不对或文件不存在

## 十、AstrBot 插件配置

AstrBot WebUI 中找到插件 `astrbot_plugin_goofish_catcher`，填写：

```json
{
  "provider_mode": "remote_rest",
  "remote_base_url": "https://worker.example.com",
  "remote_timeout_sec": 20,
  "remote_healthcheck_on_init": true,
  "remote_healthcheck_timeout_sec": 10,
  "remote_headers": [
    "CF-Access-Client-Id: YOUR_CLIENT_ID",
    "CF-Access-Client-Secret: YOUR_CLIENT_SECRET"
  ]
}
```

说明：

- `remote_api_key` 留空
- `remote_headers` 是 AstrBot 发给 Cloudflare Access 的认证头列表
- 这个配置不是写到 `data/cmd_config.json`
- `data/cmd_config.json` 是 AstrBot 全局命令配置，不是本插件远程配置

保存后重载插件。

## 十一、AstrBot 侧验证

执行：

```text
/闲鱼 状态
```

预期应看到：

- `Provider：remote_rest`
- `Provider 可用：True`
- `远程地址：https://worker.example.com`
- `远程健康详情：ok=True, provider=playwright_local, auth=disabled, storage_state=yes`

然后再验证一次实际搜索：

```text
/闲鱼 查询 iPhone
```

如果远程登录态有效，应该会正常返回搜索结果或推荐摘要。

## 十二、推荐的排查顺序

如果远程模式不工作，按这个顺序查：

1. 远程主机本机执行 `curl http://127.0.0.1:8787/health`
2. 确认 `storage_state` 是否为 `true`
3. 本地执行带 Cloudflare 头的 `/health`
4. 本地执行带 Cloudflare 头的 `/v1/search`
5. AstrBot 中执行 `/闲鱼 状态`

不要一上来就怀疑插件代码或 Cloudflare；先确认每一层单独可用。

## 十三、常见问题

### 1. `/health` 返回 `storage_state: false`

通常原因：

- `storage_state.json` 不存在
- `worker_config.json` 路径写错
- `storage_state_file` 和 `data_dir` 重复拼接

建议：

- `data_dir` 用 `./worker_data`
- `storage_state_file` 用 `storage_state.json`

### 2. Cloudflare 返回 `302 Found`

通常原因：

- Access 策略不是 `Service Auth`
- Service Token 没绑定到该应用

### 3. 外网返回 `401 worker authorization failed`

通常原因：

- worker 本地仍设置了 `GOOFISH_WORKER_API_KEY`
- worker 本地仍设置了 `GOOFISH_WORKER_CF_ACCESS_CLIENT_ID/SECRET`
- worker 在做不必要的二次鉴权

推荐只保留 Cloudflare Access 外层鉴权。

### 4. AstrBot 仍显示本地模式

通常原因：

- 插件配置没有保存
- 插件没有重载
- 改的是 AstrBot 全局配置文件，不是插件配置

### 5. 搜索返回 `AUTH_REQUIRED`

通常原因：

- 登录态文件失效
- 闲鱼要求重新登录
- 被风控或验证码拦截

处理方法：

```bash
uv run python save_state.py
mv ./storage_state.json ./worker_data/storage_state.json
```

然后重启 worker。

## 十四、安全建议

- `worker_config.json` 建议本地保存，不提交仓库
- `worker_config.json` 中不要长期保留已经泄露过的 `Client Secret`
- 如果 `Client Secret` 曾出现在聊天、截图或日志里，立即删除旧 token 并重建

## 十五、当前项目约定

当前远程方案的项目约定是：

- worker 本地默认读取 `worker_config.json`
- 环境变量优先级高于 JSON
- Cloudflare Access 是推荐的外层鉴权
- worker 自身二次鉴权不是必须
- 远程登录态只保留在远程主机，不与 AstrBot 主机同步
