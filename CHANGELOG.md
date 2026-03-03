# Changelog

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

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

