# Changelog

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [0.1.2] - 2026-03-07

### Added

- 新增远程 Worker 服务 `worker_server.py`，提供 `/health` 与 `/v1/search` 接口，复用现有 Playwright 抓取链路。
- 新增远程配置项：`provider_mode`、`remote_base_url`、`remote_api_key`、`remote_headers_json`、`remote_timeout_sec`、`remote_healthcheck_on_init`、`remote_healthcheck_timeout_sec`。
- 新增 Cloudflare Access 兼容能力，支持通过额外请求头注入 `CF-Access-Client-Id` 与 `CF-Access-Client-Secret`。

### Changed

- 远程 Provider 补完 `remote_rest` 闭环，支持启动期健康检查、统一错误码映射与自定义请求头合并。
- `/闲鱼 状态` 现在会额外展示远程模式地址、最近健康检查时间和远程健康详情。
- README 补充远程 Worker、Cloudflare Tunnel/Access 与 WebUI 配置说明。

### Fixed

- 修复 WebUI 无法完整配置远程 Provider 的问题。
- 修复远程模式下仅支持 Bearer/X-API-Key、无法直接接入 Cloudflare Access service token 的问题。

## [0.1.1] - 2026-03-03

### Added

- 新增 `playwright_force_direct` 配置项（默认开启），支持 Playwright 强制直连并禁用系统代理。
- 新增内置登录态脚本 `save_state.py`，可直接生成 `storage_state.json`。
- 新增/补充查询参数测试与 Playwright 行为测试，覆盖 `-p/--pages` 多种写法与直连参数。

### Changed

- `/闲鱼 查询` 参数解析增强：支持空格关键词与分页参数共存，支持 `-p 2`、`-p2`、`--pages=2`。
- `query_once` 改为贪婪关键词接收，避免命令参数被空格截断。
- README 登录态流程改为直接运行仓库内 `save_state.py`，并补充直连配置说明。

### Fixed

- 修复查询命令中 `-p` 参数在部分输入下不生效的问题。
- 修复登录态文件易失导致重启后掉登录的问题：增加稳定路径复制与回写机制。

## [0.1.0] - 2026-02-28

### Added

- 首次发布闲鱼监控插件基础能力。
- 实现订阅生命周期命令：订阅、退订、列表、暂停、恢复、立即检查、状态、明细、查询。
- 实现本地 Playwright 抓取、SQLite 持久化、调度轮询、上新/降价检测与去重通知。
- 接入 LLM 推荐与初筛链路，支持失败回退到启发式评分。
