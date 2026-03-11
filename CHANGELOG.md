# Changelog

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [1.0.3] - 2026-03-12

### Added

- 新增本地模式 `playwright_executable_path` 配置项，可指定系统 Chrome / Chromium / Edge 可执行文件路径。
- 远程 Worker 新增 `executable_path` 配置项与 `GOOFISH_WORKER_EXECUTABLE_PATH` 环境变量，支持指定浏览器可执行文件路径。

### Changed

- Playwright Provider 现在会在显式配置浏览器路径时使用 `executable_path` 启动浏览器。
- `save_state.py` 现在会优先复用本地 WebUI 配置的 `playwright_executable_path`，并在远程模式下兼容 Worker 的浏览器路径配置。
- README 与 `REMOTE_SETUP.md` 补充自定义浏览器路径配置说明与示例。

### Fixed

- 修复 `save_state.py` 无法跟随本地模式 WebUI 浏览器路径配置的问题。
- 修复 `save_state.py` 读取带 UTF-8 BOM 的 AstrBot 插件配置文件时可能失败的问题。

## [1.0.2] - 2026-03-11

### Added

- 新增 `filtered_items` 持久化表，用于缓存“首次出现且被筛掉”的商品。

### Changed

- 订阅轮询现在会先跳过已被筛掉的新商品，避免重复进入 `prefilter`。
- `llm_recommend_prompt` 默认示例改为明确要求“优先返回真正符合条件的结果”，可少于 `top_k`，也可返回 `0` 条。
- 轮询成功日志补充 `cached_skip` 统计，便于观察被缓存跳过的条目数量。

## [1.0.1] - 2026-03-09

### Added

- 新增 `llm_recommend_prompt` 配置项，可自定义商品推荐阶段的 LLM 提示词。
- 新增 `llm_prefilter_prompt` 配置项，可自定义结果筛选阶段的 LLM 提示词。

### Changed

- 推荐与筛选提示词支持模板占位符。
- 商品推荐提示词支持 `$keyword`、`$top_k`、`$candidates_json`。
- 结果筛选提示词支持 `$keyword`、`$items_json`。
- 保持默认提示词与原有 JSON 输出契约兼容，已有行为不变。

## [1.0.0] - 2026-03-09

### Added

- 新增独立远程部署文档 `REMOTE_SETUP.md`，说明远程主机、Cloudflare Tunnel、Cloudflare Access 与 AstrBot 插件配置流程。

### Changed

- AstrBot 插件配置页调整为远程优先布局，常用项标题更短，`provider_mode` 改为下拉选择。
- 远程认证头新增 `remote_headers` 列表入口，支持按行填写 `Header: Value`。
- 配置解析继续兼容旧版 `remote_headers_json`。
- README 和远程部署文档统一使用通用示例域名与占位符，避免包含个人部署信息。

### Security

- 整理 `.gitignore`，默认忽略 `worker_config.json`、`storage_state.json` 和本地研究文件，降低敏感信息误提交风险。

## [0.1.2] - 2026-03-07

### Added

- 新增远程 Worker 服务 `worker_server.py`，提供 `/health` 与 `/v1/search` 接口，并复用现有 Playwright 抓取链路。
- 新增远程配置项：`provider_mode`、`remote_base_url`、`remote_api_key`、`remote_headers_json`、`remote_timeout_sec`、`remote_healthcheck_on_init`、`remote_healthcheck_timeout_sec`。
- 新增 Cloudflare Access 兼容能力，支持通过额外请求头注入 `CF-Access-Client-Id` 与 `CF-Access-Client-Secret`。

### Changed

- 远程 Provider 补完 `remote_rest` 闭环，支持启动期健康检查、统一错误码映射与自定义请求头合并。
- `/闲鱼 状态` 现在会额外显示远程模式地址、最近健康检查时间和远程健康详情。
- README 补充远程 Worker、Cloudflare Tunnel/Access 和 WebUI 配置说明。

### Fixed

- 修复 WebUI 无法完整配置远程 Provider 的问题。
- 修复远程模式下仅支持 Bearer/X-API-Key、无法直接接入 Cloudflare Access service token 的问题。

## [0.1.1] - 2026-03-03

### Added

- 新增 `playwright_force_direct` 配置项，支持 Playwright 强制直连并禁用系统代理。
- 新增登录态脚本 `save_state.py`，可直接生成 `storage_state.json`。

### Changed

- `/闲鱼 查询` 参数解析增强，支持空格关键词与分页参数共存，支持 `-p 2`、`-p2`、`--pages=2`。
- `query_once` 改为贪婪关键字接收，避免命令参数被空格截断。
- README 登录态流程改为直接运行仓库内 `save_state.py`，并补充直连配置说明。

### Fixed

- 修复查询命令中 `-p` 参数在部分输入下不生效的问题。
- 修复登录态文件易丢导致重启后掉登录的问题，增加稳定路径复制与回写机制。

## [0.1.0] - 2026-02-28

### Added

- 首次发布闲鱼监控插件基础能力。
- 实现订阅生命周期命令：订阅、退订、列表、暂停、恢复、立即检查、状态、明细、查询。
- 实现本地 Playwright 抓取、SQLite 持久化、调度轮询、上新/降价检测与去重通知。
- 接入 LLM 推荐与初筛链路，支持失败回退到启发式评分。
