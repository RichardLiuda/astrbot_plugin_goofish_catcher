# Changelog

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [1.2.3] - 2026-03-14

### Added

- 商品页筛选新增屏蔽词，支持按空格、逗号或换行输入多个词，命中标题、描述、卖家或订阅关键词时直接隐藏商品记录。

### Changed

- 商品页筛选区重排为“检索与屏蔽”和“视图与排序”两组，减少选项堆叠，移动端和桌面端的阅读顺序都更清晰。
- 订阅条目下拉选项不再显示 UMO，避免主筛选信息过载。

## [1.2.2] - 2026-03-14

### Added

- 商品页新增“按订阅分类”视图，可从商品上下文快速聚焦到具体订阅条目并执行检查、暂停、恢复等管理动作。
- 商品列表新增排序字段、排序方向、最低价、最高价筛选，聚合商品和按订阅分类视图共用同一套查询能力。

### Changed

- 商品项长标题现在默认做截断展示，并限制主信息区最大高度，避免超长描述影响布局和可读性。

### Fixed

- 修复商品标题过长时右侧操作按钮被挤出可视区域的问题，操作列现在可稳定显示。

## [1.2.1] - 2026-03-13

### Fixed

- 修复 LLM 在推荐阶段返回合法空结果 `top: []` 时被错误判定为 `LLM_JSON_UNUSABLE` 并回退到启发式分析的问题。
- 修复“立即检查”在推荐列表为空时反馈不够明确的问题，现在会明确提示本次检查已完成且未命中可推荐条目。

## [1.2.0] - 2026-03-13

### Added

- 新增独立 Admin WebUI 管理后台，支持 API Key 登录。
- 新增总览、订阅、商品、运行状态、配置五个管理页面。
- 新增订阅增删改查、立即检查、暂停恢复、商品详情查看与运行状态查看能力。
- 新增运行时配置编辑与重载入口，可直接在 WebUI 中修改覆盖层配置。
- 新增管理后台静态资源与品牌图标，统一侧边栏、登录页和页面导航展示。

## [1.1.2] - 2026-03-12

### Added

- 新增 `llm_min_score` 配置项，可设置最终推荐结果的最低分阈值。

### Changed

- LLM 推荐与启发式推荐现在都会过滤掉低于 `llm_min_score` 的商品。
- 订阅轮询在过滤后若没有任何推荐条目，将直接跳过推送，不再发送空摘要。
- 手动“立即检查”在过滤后若没有任何推荐条目，也不会写入通知去重记录。

## [1.1.1] - 2026-03-12

### Changed

- Playwright 搜索翻页逻辑改为操作闲鱼网页底部分页器，不再依赖地址栏 `page` 参数。
- 第 2 页及后续页现在会先等待首屏结果稳定，再跳转目标页码，适配闲鱼前端通过接口 `pageNumber` 驱动分页的实际行为。

### Fixed

- 修复闲鱼 PC 搜索页在 `search?q=...&page=n` 下仍可能实际请求第一页数据的问题。
- 修复本地 Playwright 抓取多页结果时可能重复抓取第一页、导致分页失效的问题。

## [1.1.0] - 2026-03-12

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
