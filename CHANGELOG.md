# Changelog

本项目遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## 远程 Worker 兼容性

当前插件版本（v3.6.0）需要 Worker **≥ v3.5.0**。

> Worker 有 breaking change 时会同步更新此行，并在对应版本的 CHANGELOG 中注明。

---

## [Unreleased]

### Fixed（合入前集成评审修复）

- 意图引擎：预算解析全部要求上下文锚点（预算/以内/元/￥ 等），「850W电源 预算400元」不再把功率误判为预算；`require_terms` 对 LLM 返回的标量/字符串健壮化，LLM 输出解析异常一律回退启发式而不再冒泡报错。
- 聚合层：同店聚类改用完整规范化标题做键（不再截断 12 字符，同店 5090/5080 不同型号不再误并），被归并的商品保留在 `other_items` 中不再凭空消失；LLM 依「宁缺毋滥」返回空推荐时尊重该结论（不再回退启发式强行推荐），LLM top 中重复 item_id 去重。
- 采购编排：平台在降级后成功时清除其早期级别的失败记录，决策卡片不再同时展示某平台的商品与「失败平台」警告。
- 引擎（闲鱼行为回归修复）：恢复 `check_login_state` 的未初始化守卫并覆盖浏览器已死状态——心跳探测不再自动拉起被用户关闭的浏览器窗口（搜索路径的自动重拉保留）；`validate_login` 的验证码判定恢复 master 窄口径（3 标记、仅前 3 个 ret 项），mtop 限流不再把成功登录误判为 CAPTCHA；详情页标题回退提取补 HTML 实体反转义。
- 引擎（平台化盲区）：URL 级登录墙/验证码判定改走注入档案的钩子（淘宝档案的 `is_auth_url`/`is_captcha_url` 不再是死代码）；`SiteProfile` 新增 `llm_login_check_enabled`（淘宝置 False，访客态搜索不再被 LLM 登录判定误杀为 AUTH_REQUIRED）；LLM 兜底提取与 payload 提取路径按平台前缀化 item_id、URL 经 `build_item_url` 构建（淘宝商品不再以裸 ID + 闲鱼 URL 入库）。
- 集成层：批量『/闲鱼 立即检查』、WebUI 手动检查、深度分析兜底均按订阅/商品平台路由 provider，平台不可用时明确报错，绝不静默回退闲鱼搜索（消除跨平台数据污染）；心跳登录失败仅暂停 goofish 订阅（淘宝订阅不再被连坐后无法恢复）；自动快速登录成功仅恢复对应平台的暂停订阅；admin 订阅摘要新增 `platform` 字段；『/闲鱼 列表』纯闲鱼输出恢复 master 原格式（仅非闲鱼订阅行加平台前缀）；『/闲鱼 明细』提示仅对闲鱼订阅输出。
- 存储：v7 迁移的 `market_price` 换表改为幂等（`INSERT OR IGNORE` + 覆盖中断窗口），迁移中途进程被杀后重启不再因主键冲突卡死。
- 测试卫生：所有安装 astrbot 桩的测试文件改为「真实 astrbot 可导入时不装桩」，全量 `unittest discover` 在 AstrBot 环境不再互相污染。
- 仓库卫生：移除贡献者个人 AI 工具链残留（`.kimi/`、`skills/neat/`、`pyproject.toml` 脚手架）。

### Changed

- 多平台改造阶段 0.1（数据层平台维度）：`subscriptions` 表新增 `platform` 列（默认 `goofish`），唯一键由 `(umo, keyword)` 重建为 `(umo, platform, keyword)`；`market_price` 表主键重建为 `(platform, keyword)`，老数据自动归入 `goofish`（数据库迁移 v7，老库平滑升级，无需人工干预）。
- `Subscription` / `NormalizedItem` / `MarketPrice` 数据类新增 `platform` 字段；存储层订阅与市场均价接口支持按平台读写，现有调用方（`/闲鱼` 命令、llm_tool、Admin WebUI）行为不变。
- 多平台改造阶段 0.2（item_id 前缀化）：`goofish_analyze_item_detail` 等处的商品 URL 构建收口到平台注册表 `build_item_url()`，闲鱼 URL 输出不变。
- 多平台改造阶段 0.3a（引擎/档案拆分）：`provider_playwright.py` 的平台特数据（搜索 URL 构建、登录/验证码判定、收藏按钮与分页选择器、过滤文案、日志白名单）全部改读 `GOOFISH_PROFILE`；`PlaywrightSearchProvider` 新增可选 `profile` 注入参数（默认闲鱼档案，现有调用方零改动）；`login_session.py` 的重复常量收敛为档案别名。行为保持型重构，运行时行为零变化。
- 多平台改造阶段 1.5b（插件内淘宝订阅）：`build_providers()` 按平台构建 provider 路由表（淘宝 provider 使用独立的 `storage_state.taobao.json` 与 `browser_profile_taobao/`，远程模式跳过）；scheduler 按 `sub.platform` 路由搜索与深度分析，平台无 provider 时自动暂停并告警（PLATFORM_UNAVAILABLE）；淘宝详情深度分析按 `supports_item_detail=False` 短路返回"暂未支持"；`goofish_create_subscription` 新增 `platform` 参数（默认 goofish）；Admin 侧校验：淘宝未启用报错、轮询间隔下限 1800s、订阅平台不可修改；通知推送头按平台显示（如【淘宝建议】）；引用回复收藏淘宝商品时提示"该平台收藏暂不支持"并跳过；新增配置项 `taobao_enabled`（默认 false，四处已同步）。
- 本地实验台新增 `watch-taobao` 轮询监控命令（复用存储与检测链路，用于实测淘宝风控容忍频率）。
- 多平台改造 P0（登录认证链路平台化）：`GoofishLoginSession` / `LocalAuthSessionController` / `RemoteAuthRecoveryCoordinator` 全部按平台注入站点档案——淘宝订阅触发 AUTH_REQUIRED 时推送**淘宝**登录二维码（落地页 `login.taobao.com`，校验接口 `mtop.user.getusersimple`），扫码确认后**只恢复同平台订阅**；`goofish_start_login` / `goofish_check_login` 新增 `platform` 参数（默认 goofish）；淘宝会话独立存储于 `storage_state.taobao.json` 与 `browser_profile_taobao/`；修复 quick-login 在淘宝访客态的误判成功（`SiteProfile.quick_login_enabled`，淘宝关闭）；修复恢复订阅时丢失 `platform` 字段的既有 bug；新增 `test_platform_auth_flow.py`（15 用例），并顺带修复 3 个 test_remote_auth_flow 既有测试错误。闲鱼登录行为逐字节不变。
- P0 实测修复：`SiteProfile` 新增 `validate_probe_url`（登录落地页与登录态探测页分离）——淘宝登录页是纯登录页，登录态校验改走搜索页（`mtop.user.getusersimple` 仅在内容页触发）；真实淘宝登录态下有头搜索验证通过（无滑块）。
- P1 体验修复（AstrBot 实测反馈）：`check_subscription` 按平台路由 provider，重复触发返回友好提示而非报错；`check_login_state` 冷启动不再直接报 error；淘宝间隔下限改为可配置 `taobao_min_interval_sec`（创建/更新一致生效）；不支持详情分析的平台跳过节流 sleep 与占位缓存；浏览器被用户手动关闭后自动检测并重拉（不再连环 UNKNOWN 报错）。
- 2.x 冒烟修复：意图启发式的预算识别改为必须有上下文锚点（预算/以内/元，修复"RTX 5090"被误吞为预算 ¥5090）；单平台搜索超时默认 10s→20s（对齐引擎真实耗时）；`SiteProfile.auth_on_payload_markers`（淘宝=False）——访客可用平台不再因次要接口的 SESSION_EXPIRED 误判 AUTH_REQUIRED，只认真登录墙重定向。
- 阶段 1.3（淘宝详情分析）：`SiteProfile.parse_detail_page` 详情页解析钩子（闲鱼默认路径零改动）；淘宝详情页实测为 SSR（无详情 mtop 接口），解析 HTML 内嵌 `var b={...}` JSON（`loaderData.home.data.res`）——提取店铺三件套（sellerNick/DSR 三项/creditLevel/体验分）、SKU 全档真实价目表（props 维度解码 + sku2info 价格库存，skuId/下标双键兼容）、主图；信用规则（DSR 全 ≥4.8→good、有 <4.5→bad、旗舰店上调）；风险提示（C店低分/SKU 价差>3 倍引流/部分档位无货）；`TAOBAO_PROFILE.supports_item_detail=True`（调度器对淘宝订阅恢复真实深度分析，替代原"暂未支持"占位）。
- 阶段 0.3b（详情解析入档案，纯重构零行为变化）：闲鱼详情解析四件套（`_build_deep_analysis_result`/`_find_item_detail_payload`/`_classify_credit`/`_extract_image_urls`）从引擎逐字迁入 `app/platforms/goofish.py` 并接成 `GOOFISH_PROFILE.parse_detail_page`，引擎 `analyze_item_detail` 两平台统一走钩子（留 re-export 别名，既有测试零改动）；`_payload_indicates_captcha` 统一为 8 标记版（删除 login_session 私有 3 标记版）。
- 聚合层同店聚类：决策管线新增 `cluster_same_shop`——同平台内同店铺且标题主键相似的商品归并为一条（保留最高分者），卡片标注"同店同款 ×N / 同店最低 ¥X"，top 推荐不再被同店引流链接刷屏。
- 多平台改造阶段 1.1（淘宝搜索适配）：`app/platforms/taobao.py` 淘宝档案落地——`SiteProfile` 新增 `parse_dom_card` / `dom_card_extractor_js` 可选钩子，淘宝 SSR 搜索页走 DOM 定制提取（title 属性取标题、priceInt+priceFloat 拼价格、店铺名/销量进 `raw`），`click.simba.taobao.com` 广告链接在选择器层与解析层双重过滤；`extract_item_id_from_url` / `normalize_url` 下沉至 `platforms/registry.py` 共享；错误消息按 `profile.display_name` 参数化（不再硬编码 "goofish"）。本地实测淘宝搜索返回正确结果（访客态，滑块手动过后）。淘宝商品 ID 带 `taobao:` 前缀，与闲鱼 ID 空间隔离。已知边界：分页与价格 URL 参数未实测（单页搜索 + 内存过滤兜底）；列表价为 SKU 区间最低价。

### Added

- 新增 `test_storage_platform.py`：覆盖 v7 schema、同关键词跨平台订阅、市场均价按平台隔离、v6 老库迁移升级。
- 新增 `test_scheduler_platform_routing.py`（阶段 1.5b）：provider 路由表构建、淘宝深度分析短路、scheduler 双平台路由与 PLATFORM_UNAVAILABLE 暂停。
- 新增 2.x 采购决策管线：`app/intent/engine.py`（LLM 意图解析 + 降级阶梯，启发式兜底）、`app/aggregator/aggregate.py`（去重/风险标签/LLM+启发式排序）、`app/reporter/card.py`（Markdown 决策卡片，含降级提示与"N 条未进推荐"平台露面）、`app/purchase.py`（编排服务：并发搜索→空结果逐级降级→聚合排序，单平台超时/异常隔离）；`main.py` 新 llm_tool `buyagent_purchase_decision`（自然语言→决策卡片，合并转发/纯文本发送）；`scripts/local_lab.py` 新增 `decide` 命令（支持 `LAB_LLM_*` 环境变量接任意 OpenAI 兼容 LLM，无配置走启发式）。配套 `test_purchase_decision.py`（31 用例）。
- 新增 `test_taobao_detail.py`（阶段 1.3，31 用例）：淘宝详情解析（店铺类型/DSR/SKU 价目/价差风险/烂结构兜底）；local_lab 新增 `probe-detail`（详情页结构侦察）与 `detail-taobao`（详情分析验证）命令。
- skills 文档多平台化：新增 `skills/purchase.md`（决策卡片工具说明）与 `skills/platforms.md`（多平台机制/能力矩阵/淘宝数据真相，含淘宝使用流程与数据流说明）；`skills/README.md` 决策树与工具表覆盖全部 18 个工具；subscribe/favorite/search/data-and-status 四篇补充平台参数与淘宝边界。
- 决策报告新增 `other_items`（未进 top_k 的候选简表），`buyagent_purchase_decision` 返回给 LLM 的摘要附带该简表——用户追问"未进推荐的都有啥"时 LLM 可直接回答（此前摘要只有数量，LLM 只能重新搜索）。
- 新增 `app/platforms/registry.py`（阶段 0.2）：item_id 平台归属规则（裸 ID 视为 goofish 以兼容存量，新平台必须带 `{platform}:` 前缀）与商品 URL 构建的唯一收口；`make_item_id` / `split_item_id` / `build_item_url` / `platform_display_name`。配套 `test_platform_registry.py`。
- 新增 `app/platforms/base.py` 与 `app/platforms/goofish.py`（阶段 0.3a）：`SiteProfile` 站点档案数据类（21 个数据字段 + 4 个钩子函数）与闲鱼档案实例，为未来淘宝等档案的接入点。
- 新增 `app/platforms/taobao.py`（阶段 1.1）：淘宝档案与 DOM 提取钩子；配套 `test_taobao_profile.py`；`scripts/local_lab.py` 新增 `search-taobao` 命令与 sso 探针自动轮询过验证能力。
- 新增 `scripts/local_lab.py` 本地实验台（登录/搜索/SSO 探针）。

---

## [3.6.0] - 2026-07-11

### Added

- WebUI 商品列表新增"深度搜索"筛选（全部 / 已深度搜索 / 未深度搜索），聚合视图与按订阅分组视图均支持，并在表格中新增"深度搜索"状态列。
- WebUI 商品详情页的"深度分析"卡片新增手动触发按钮：对尚未深度搜索过的商品可一键触发一次深度分析，完成后直接同步展示最新结果，无需手动刷新。

### Changed

- 手动触发深度搜索命中闲鱼滑块验证/风控时，WebUI 会给出明确提示（本功能不会自动完成验证，需稍后重试或重新登录），并在触发按钮旁提示该操作存在触发滑块验证的风险。
- 本功能复用现有 `provider.analyze_item_detail` 逻辑，本地与远程 Worker 模式均无需升级 Worker。

---

## [3.5.0] - 2026-07-01

> **⚠️ Worker 端行为变更，`remote_rest` 模式需在 Worker 服务器上 `git pull` 并重启。**

### Added

- 新增浏览器代理配置（`playwright_proxy`）：支持将 Playwright 浏览器的所有出站流量路由到指定上游代理（SOCKS5 / HTTP），可通过 `worker_config.json` 的 `playwright_proxy` 字段或环境变量 `GOOFISH_WORKER_PROXY` 配置。
- AstrBot 插件配置面板新增"浏览器代理"配置项（`playwright_proxy`），本地模式下同样生效。
- 登录态生成（`save_state.py` / Worker 在线扫码登录）同步使用相同代理，确保 cookie 绑定到与搜索请求相同的出口 IP。

### Changed

- `REMOTE_SETUP.md` 新增代理配置章节，补充云服务器（无桌面环境）部署说明，包括 xvfb 安装、系统库依赖、`xvfb-run` 用法，以及数据中心 IP 风控的根因分析和解决路径。

---

## [3.4.2] - 2026-06-30

### Fixed

- 修复实时搜索（`goofish_search_live`）返回给 LLM 的文本不含价格数据，导致 LLM 凭训练知识臆测价格区间的问题；现在 LLM 工具返回值中会附带真实的价格区间与均价。

---

## [3.4.1] - 2026-06-29

### Fixed

- 修复 WebUI 商品管理删除商品时请求体被重复 JSON 序列化，导致后台返回 422、商品无法删除的问题。

---

## [3.4.0] - 2026-06-28

### Added

- 新增 `goofish_query_recommend` LLM 工具，可实时搜索并按推荐价格阈值、筛选条件和 Top K 返回推荐结果。
- 新增 `goofish_analyze_item_detail` LLM 工具，可对单个商品执行或复用深度分析，返回卖家信用、主图、想要人数、浏览量和风险结论。
- 新增 `goofish_get_subscription_analytics` LLM 工具，便于查询订阅价格趋势、市场均价、通知趋势和最近推荐记录。
- 新增 VitePress 风格 T2I 文档模板，支持深色主题、代码块语言标识和数学公式渲染。

### Changed

- LLM 订阅创建、更新和列表工具支持展示与维护推荐最高价阈值；临时推荐查询支持自定义推荐数量。
- 调度器对连续超时、网络错误和未知异常新增分级告警，订阅不暂停时也会在连续失败达到阈值后提示用户。
- 同步默认 AstrBot 命令配置项，适配新版 WebSearch、Admin、CUA 和指标开关配置。

### Fixed

- 修复临时推荐查询中 `recommend_max_price=0` 被当作 0 元阈值导致所有商品被过滤的问题。
- 修复商品深度分析工具遇到已缓存的拒绝结果时可能重复打开详情页的问题，降低触发风控的概率。
- 修复 VitePress T2I 模板对 Markdown HTML 直接写入页面带来的脚本注入风险。

---

## [3.3.2] - 2026-06-26

> **⚠️ Worker 侧修复，`remote_rest` 模式需同步更新 Worker。**

### Fixed

- 修复深度分析误取推荐流卖家导致卖家信用显示 `unknown` 的问题：详情页现在优先绑定 `mtop.taobao.idle.pc.detail.data.sellerDO`，避免拿到同页推荐商品的 `cardData.user`。
- 增强卖家信用提取和判定：补充好评率、卖出数、注册天数、闲鱼信用等级、芝麻/实人认证等结构化字段解析。
- 修复详情主图提取顺序，优先使用 `itemDO.imageInfos` 中的主图，避免通知图片错位。
- 深度搜索触发闲鱼滑块/风控时不再继续批量打开详情页，也不再写入 `unknown` 缓存；改为进入冷却并保守跳过剩余详情分析。
- 降低深度搜索触发风控概率：详情分析候选数减少到 3 个，并加入 8-15 秒随机间隔。
- 修复推荐消息发送失败后 NEW 事件被 `items` 表吞掉的问题：未成功写入通知记录的新商品 24 小时内会自动恢复为候选。
- 修复 WebUI/通知使用非法 `umo` 时反复抛长 traceback 的问题，并在订阅保存时校验 `unified_msg_origin` 格式。
- 修复收藏链路登录恢复误判：收藏遇到 `AUTH_REQUIRED` 时会先尝试快速登录并重新加载商品详情；登录恢复页若已经是登录态，不再发送二维码截图。

### Added

- 新增深度分析和风控诊断日志，便于定位详情 payload、卖家信用、缓存命中/重试和风控冷却状态。

---

## [3.3.1] - 2026-06-26

### Changed

- 增强订阅统计价格趋势图：改为每日均价线 + 中位数虚线 + 最低/最高区间带，并新增渐变面积、网格线、坐标刻度、日期标签、图例和最新数据高亮。
- 增强近 30 天通知趋势图：改为上新/降价堆叠条，并增加上新总数、降价总数、近 7 天合计等摘要卡片。
- 订阅统计价格均值和极值展示新增 IQR 离群值过滤，避免极端异常挂价污染图表和统计摘要。

## [3.3.0] - 2026-06-26

> **⚠️ Worker 端行为变更，`remote_rest` 模式需在 Worker 服务器上 `git pull` 并重启。**

### Added

- 新增订阅高级筛选能力：个人闲置、包邮、新发布范围、地区筛选，并贯通本地 Playwright、远程 Worker、Admin API、LLM 工具与 WebUI 临时查询。
- 新增候选商品深度分析：推荐前抓取详情页，缓存主图、卖家信用、想要人数、浏览量与风险结论；明确低信用或严重风险商品会在推荐前过滤。
- WebUI 新增订阅统计弹窗，展示历史价格折线图、价格样本统计、近 30 天通知趋势与最近推荐商品。

### Changed

- 推荐通知与查询推荐消息改为同一消息链内展示文字、主图、深度分析摘要和商品链接；图片发送失败时自动降级为文字 URL。
- 商品详情抽屉展示深度分析卡片，临时查询与订阅列表同步展示高级筛选和深度分析摘要。
- `remote_rest` Worker 新增深度分析接口，并支持接收高级筛选参数。

### Fixed

- 深度分析失败或信用信息缺失时改为保守放行，避免因详情页临时异常误杀候选商品。

## [3.2.0] - 2026-06-25

### Added

- **市场均价持续监控**：新增 `market_price` 表，每次抓取后用本批商品价格的中位数通过指数移动平均（EMA，α=0.15）滚动更新关键词级别市场参考价，数据随时间平滑积累，不受单次异常价格干扰
- **价格波动分析**：历史价格统计（`price_history`）新增批量聚合查询（MIN/MAX/AVG/COUNT），`PriceDropDecision` 新增 `below_hist_min` 标记，当前价低于历史最低价时自动标注
- **推荐评分引入市场维度**：启发式评分新增市场均价对比（低于市场均价最多 +12 分，高出 20% 以上最多 -10 分）、历史最低价突破加分（最多 +10 分）；同时修正了降价幅度的重复计分问题（绝对值与百分比原先各贡献 25 分，现改为百分比主导最多 40 分 + 金额辅助最多 10 分）
- **价格异常检测**：价格暴涨超过上次的 10 倍时记录 WARNING 日志并跳过降价判断，防止卖家改错价触发假降价通知
- **LLM 推荐上下文增强**：传给大模型的候选商品 JSON 新增 `hist_min`、`hist_avg`、`market_price` 字段，大模型可参考历史与市场基准作出更准确的推荐

### Changed

- `notification_meta` 新增 `hist_min`、`hist_avg`、`below_hist_min`、`market_price` 字段，方便事后审计与 WebUI 展示

## [3.1.3] - 2026-06-24

> **⚠️ Worker 端行为变更，`remote_rest` 模式需在 Worker 服务器上 `git pull` 并重启。**

### Fixed

- 订阅页数上限默认值从 2 提升至 8，本地端与 Worker 端同步更新，避免用户未配置 `max_pages` 时被意外限制为 2 页
- **[Worker 侧]** `max_retries` 从硬编码 0 改为可配置（默认 3，与本地端对齐），同时 `retry_base_sec` / `retry_max_sec` 也支持通过配置文件或环境变量覆盖（`GOOFISH_WORKER_MAX_RETRIES` 等）

## [3.1.2] - 2026-06-23

> **⚠️ 全部为 Worker 侧修复，`remote_rest` 模式需在 Worker 服务器上 `git pull` 并重启。**

### Fixed

- **[Worker 侧]** 修复 Session 过期后点击「快速进入」弹窗仍中断任务的问题。之前登录成功后未重新加载搜索页，直接使用登录前的空 payload 导致 0 结果；同时清除了登录页触发的 captcha 误报 flag。
- **[Worker 侧]** 新增对浏览器凭 cookie 自动静默登录场景的支持：mini_login iframe 自动消失（无需点击按钮）时也视为登录成功，不再误抛 AUTH_REQUIRED。
- **[Worker 侧]** 修复 `page.accessibility.snapshot()` 在 Playwright ≥ 1.35 中已被移除导致的警告，改用 `page.locator("body").aria_snapshot()`，旧版本自动 fallback。



> **⚠️ Worker 侧修复，`remote_rest` 模式需在 Worker 服务器上 `git pull` 并重启。**

### Fixed

- **[Worker 侧]** 修复点击「快速进入」弹窗后任务中断的问题。登录成功后原先直接使用登录前的空 payload 继续执行，导致 0 结果；现修复为清空旧 payload 并重新加载搜索页，确保登录后正常返回商品。

## [3.1.0] - 2026-06-23

> **⚠️ 使用 `remote_rest` 模式的用户：本版本包含价格解析修复，修复位于 `app/provider_playwright.py`（Worker 侧代码）。更新插件后请同步在 Worker 服务器上执行 `git pull` 并重启 Worker 进程，否则价格显示仍不正确。**

### Added

- WebUI 商品记录页支持多选批量删除和单条行内删除，删除前有确认对话框。
- 后端新增 `DELETE /api/items` 接口，支持按 item_id 列表批量删除商品记录（含关联价格历史）。

### Changed

- 商品记录页搜索过滤区重新设计为两行紧凑工具栏，去掉外置标签和多行提示文字，改用 placeholder，高度缩减约 75%。
- 过滤字段间距、内边距整体收紧，界面更紧凑。

### Fixed

- **[Worker 侧]** 修复价格解析错误导致商品价格显示为 1 元的问题。根本原因是闲鱼搜索 API 的 `price` 字段为富文本 list 格式，旧逻辑取第一个 token `"1"` 就返回，修复后先拼接所有 token 再解析。**`remote_rest` 模式需同步更新 Worker。**
- **[Worker 侧]** 修复 `_extract_price` 字段优先级：`priceText`/`displayPrice` 等展示字段现在优先于裸整数 `price` 字段。
- **[Worker 侧]** 修复 `_parse_price` 使用万/千倍数时的浮点精度问题，避免价格范围过滤误判。

## [3.0.3] - 2026-06-23

### Fixed

- 修复价格解析错误导致商品价格显示为 1 元的问题。根本原因是闲鱼搜索 API 的 `price` 字段返回富文本 list 格式（`[{"type":"integer","text":"1"}, {"type":"decimal","text":".58"}, {"type":"unit","text":"万"}]`），旧逻辑逐项遍历找到第一个 dict 的 `text` 字段 `"1"` 就返回 `1.0`，修复后先拼接所有 token 再解析，正确得到 `15800.0`。
- 修复 `_extract_price` 字段优先级错误：`priceText`/`displayPrice` 等展示字段现在优先于裸整数 `price` 字段，避免内部标记字段覆盖真实价格。
- 修复 `_parse_price` 使用万/千倍数时的浮点精度问题（如 `1.62 * 10000 = 16200.000000000002`），对结果加 `round(..., 2)`，避免价格范围过滤误判。

## [3.0.2] - 2026-06-22

### Fixed

- Admin WebUI 配置页新增"后台监听地址"（`admin_webui_host`）选项，Docker 部署时可在 UI 中直接改为 `0.0.0.0`，无需手动编辑配置文件；修复默认绑定 `127.0.0.1` 导致容器外反向代理 502 的问题。

## [3.0.1] - 2026-06-20

### Fixed

- `goofish_search_live` 和 `/闲鱼 查询` 的价格过滤现在通过 URL 参数（`priceLower`/`priceUpper`）传递给闲鱼服务器端，解决了低价配件占据搜索前排导致价格过滤后 0 结果的问题。
- Admin WebUI 启动失败时补充错误日志，方便排查端口占用等问题。

## [3.0.0] - 2026-06-19

> **⚠️ 升级注意：如果你使用 `remote_rest` 模式，请务必同时更新远端 Worker 代码至同版本。** 本版本重构了浏览器 Agent 相关接口（新增 `AgentRequest`），旧版 Worker 与新版插件不兼容。

### Added

- **远程 Agent 执行**：远端 Worker 新增 `AgentRequest` 接口，支持将 `goofish_browser_task` 的 Agent 任务完整卸载到 Worker 机器；远程模式下本地插件进程不再需要 Playwright。
- **浏览器 Agent 强化**：新增 `extract_items` 快速提取商品列表动作；Agent 执行进度实时推流至对话界面，LLM 可接收执行结果并继续推理；向 Agent 系统提示注入已验证的抓取脚本，提升 ReAct 循环效率与稳定性。
- **`goofish_search_live` 工具**：新增 LLM 可调用的快速脚本化搜索工具，支持引用回复序号收藏；定位为日常搜索的首选工具，区别于面向复杂页面任务的 `goofish_browser_task`。
- **快速进入自动点击**：二维码扫码成功后，自动检测并点击「快速进入」按钮，完成认证恢复，减少需手动介入的情况。
- **aiocqhttp 合并转发消息**：使用 aiocqhttp 渠道时，`/闲鱼 查询` 和 `goofish_search_live` 的商品列表以合并转发消息形式发出，防止刷屏；引用转发消息回复序号仍可触发收藏（基于会话缓存匹配）。
- **Cloudflare Access 配置优化**：「远程 Header」从逐行 `Key: Value` 文本框拆分为独立的 `CF-Access-Client-Id` / `CF-Access-Client-Secret` 输入字段，更易填写；旧格式仍向下兼容。
- **订阅操作人工确认**：`goofish_create_subscription`、`goofish_delete_subscription`、`goofish_update_subscription` 工具要求 LLM 在执行前先向用户确认，避免误操作。
- **`skills/` 文档目录**：新增覆盖全部 LLM 工具的详细使用指南（订阅规则、搜索工具、Agent 使用场景），作为 Agent 推理的唯一参考来源。

### Changed

- 插件设置页精简，Agent 相关开关合并为单一「启用浏览器 Agent」选项，减少配置项数量。
- 浏览器 Agent 定位明确为"处理无法用固定脚本完成的不规则任务"的兜底工具，`skills/` 说明中已更新适用场景划分。

### Fixed

- 修复 Playwright >=1.41 兼容性问题。
- `goofish_search_live` 的 `pages` 参数类型从 `integer` 改为 `number`，修复部分 LLM 传参时的类型不匹配。

## [2.3.0] - 2026-06-16

### Added

- 心跳检测：playwright_local 模式下每 30 分钟主动探测一次登录态，检测到会话失效时自动暂停所有订阅、触发登录恢复流程并广播告警通知，无需等到下次定时抓取才发现掉线。
- LLM Agent 降级兜底：当 CSS 选择器因闲鱼前端更新而失效时，自动回退到 AX Tree + LLM 提取商品列表、检测登录状态及定位收藏按钮，提升对前端变更的健壮性。
- `Notifier` 新增 `broadcast_alert` 方法，支持向多个用户批量广播告警消息。
- `Storage` 新增 `pause_all_enabled_subscriptions` 及 `get_all_subscriber_umos` 方法，供心跳检测批量操作使用。

### Fixed

- 关键词预筛（prefilter）被拒绝的价格合规商品现在也会写入 `items` 表，确保所有符合价格区间的商品均有数据库记录，便于后续价格趋势等分析功能使用。此前这些商品仅进入 `filtered_items` 去重缓存，价格字段缺失。

## [2.2.5] - 2026-06-11

### Added

- `/闲鱼 查询` 支持 `--min-price`/`--max-price`（别名 `--min`/`--max`）按价格区间过滤结果，结果头部展示生效的价格区间，`可再次执行` 提示也会携带价格参数。

### Fixed

- `/闲鱼 立即检查`、`退订`、`暂停`、`恢复` 命令的关键词参数从 `str` 改为 `GreedyStr`，现在支持含空格的多词关键词（如 `尼康 z8`）。

## [2.2.4] - 2026-06-11

### Fixed

- 修复从 v2.2.2 升级后，在 WebUI 设置订阅最低价/最高价时触发 500 错误的问题。根本原因是 v2.2.3 将 `price_min`/`price_max` 两列的数据库迁移错误地并入了已执行过的迁移版本 3，导致升级用户的数据库缺少对应列；修复方式为将这两列提取至新的迁移版本 4，并兼容已误跑过旧迁移的情况。

## [2.2.3] - 2026-05-30

### Added

- 订阅条目新增「最低价 / 最高价」过滤：超出区间的商品不会再触发上新或降价候选。WebUI 编辑订阅时可填写两端，留空或 0 表示不限。

## [2.2.2] - 2026-04-19

### Added

- 新增订阅级“推荐最高价”阈值，支持在 WebUI 中为单条订阅设置推荐价格上限；超过阈值的商品将不会进入最终推荐结果。

## [2.2.1] - 2026-04-12

> 注意：如果你使用 `remote_rest` 模式，请同时将 worker 侧代码仓同步到 `2.2.1` 或更新版本；本次修复发生在远端 worker 实际执行的分页抓取逻辑中，若主端与 worker 版本不一致，远程模式下可能仍会出现旧问题。

### Changed

- 将 `worker_data/` 目录加入 `.gitignore`，避免远端 worker 运行时生成的本地状态文件被误纳入版本控制。

### Fixed

- 修复请求第 2 页及之后的搜索结果时，如果闲鱼实际并不存在对应分页，流程仍继续等待分页激活态并最终超时的问题；现在会将“无此页”视为正常空结果处理，不再误报超时。

## [2.2.0] - 2026-04-11

> 注意：如果你使用 `remote_rest` 模式，请同时将 worker 侧代码仓同步到 `2.2.0` 或更新版本；本版本调整了远端登录与收藏工作流，若 AstrBot 插件与 worker 版本不一致，可能无法正常运行。

### Added

- 新增“引用推荐消息回复序号即可收藏”能力，支持对单条推荐列表直接回复 `1`、`1 3`、`1,2` 等格式批量收藏商品。如果推送列表直接看中的话，再也不用点进去登录之后才能收藏了！
- 新增收藏能力抽象，`playwright_local` 与 `remote_rest` 均支持按商品链接执行收藏。
- 新增远端 worker 收藏接口 `/v1/favorite`，并补充引用收藏、远端登录与收藏流程的回归测试。

### Changed

- 推荐消息尾部补充“引用本消息回复序号可收藏”的操作提示，覆盖查询推荐与主动推送场景。
- 本地与远端登录流程统一改为直接接管扫码成功的活跃 Playwright 会话，不再依赖“保存后关闭再重开”的不稳定路径。
- Playwright provider 收紧为单浏览器实例串行执行查询与收藏，降低重复拉起浏览器导致的验证风险。
- 远端登录确认、收藏执行与页面状态探测补充更细粒度诊断日志，便于排查登录态、验证码与嵌入式登录框问题。

### Fixed

- 修复引用推荐消息回复序号时，消息可能先被 AstrBot 默认 LLM 聊天链路接管，导致收藏逻辑未触发的问题。
- 修复闲鱼商品详情页出现嵌入式 `mini_login` 登录框时，原流程无法稳定识别登录失效的问题。
- 修复扫码后本地/远端登录态在保存或会话切换后容易立即过期，导致查询与收藏再次触发补登录的问题。
- 修复登录页信号识别过宽造成的误判，避免普通配置接口或页面文案被错误当成未登录状态。

## [2.1.1] - 2026-03-27

### Fixed

- 修复补登录态期间再次发送登录命令时的判定边界，避免 `/闲鱼 登录完成`、`/闲鱼 登录取消` 等显式命令被误识别为“重启登录”。

## [2.1.0] - 2026-03-26

### Changed

- 本地模式 `playwright_local` 现在与 `remote_rest` 统一走对话内补登录态链路，支持二维码截图下发、扫码后回复任意消息继续、自动恢复暂停订阅。
- 本地登录态改为固定使用插件稳定路径 `plugin_data/storage_state.json`，不再依赖配置页手动指定登录态文件。
- WebUI 配置页移除 `playwright_storage_state_file`，本地模式默认直接走统一登录流程，减少配置分叉。
- README 与配置参考同步更新为统一登录说明，本地主路径改为 `/闲鱼 登录`，`save_state.py` 保留为备用 CLI 方式。

## [2.0.0] - 2026-03-26

### Added

- 新增远端登录恢复会话链路：`remote_rest` 模式下可自动启动远端登录窗口、回传二维码截图，并在扫码后自动保存远端登录态。
- 新增远端补登录态的会话控制接口 `/v1/auth/start`、`/v1/auth/confirm`、`/v1/auth/cancel`。
- 新增 `CONFIG_REFERENCE.md`，将详细配置说明从 README 中拆出，单独维护。

### Changed

- `CAPTCHA` 处理改为先自动重试 2 次，再进入补登录态流程。
- 远端补登录态流程改为“扫码后在同一会话回复任意消息即可继续”，不再依赖复杂确认指令。
- 补登录态期间队列会暂停等待，避免未恢复登录态时继续消耗任务。
- 抓取总超时改为按 CAPTCHA 重试总预算计算，避免本地外层超时先于远端真实错误返回。
- README 从环境要求到常见问题排查部分重写为精简导航版，并把复杂配置拆到子文档。

### Fixed

- 修复远端 worker 已经弹出登录页时，AstrBot 侧仍可能先收到 `TIMEOUT` 而不是 `AUTH_REQUIRED` / `CAPTCHA` 的问题。
- 修复 `立即检查`、`查询` 与调度链路在 CAPTCHA 多次重试时，仍沿用旧的 50 秒外层超时预算导致流程被提前截断的问题。
- 修复补登录态期间普通回复与命令消息的判定边界，避免 `/闲鱼 登录` 等命令被误当成“已登录”确认。

## [1.3.1] - 2026-03-18

### Changed

- 收紧移动端 WebUI 的整体间距、顶部栏和表单控件尺寸，在手机视角下提高信息密度。
- 运行状态页重排桌面端左右分栏比例，并压缩“状态摘要”卡片的布局占用，减少留白过大的问题。
- 统一优化移动端表格布局策略，窄屏下优先保持列宽和关键信息完整，不再把列表内容硬挤成竖排拆字。
- 商品页筛选区、最近抓取记录、订阅列表等区域补充更灵活的响应式布局与滚动策略，整体观感更协调。
- 商品列表在手机端对超长商品名改为稳定的两行折叠展示，避免主列被异常撑宽。
- 运行监控浮窗补充移动端专属收纳态布局，并调整为手机端默认收起。

## [1.3.0] - 2026-03-17

### Added

- 新增全局运行监控浮窗，统一展示订阅检查、手动检查与临时查询在抓取、预筛、分析三个阶段的实时状态。
- 新增活动监控接口 `/api/activity-monitor`，供 WebUI 在不同页面持续展示当前执行中的任务。

### Changed

- 临时查询状态提升为全局状态，切换页面后仍会保留“分析中”状态与最终结果。
- 运行状态页与总览页的认证状态改为读取统一健康快照，并自动按周期同步，避免显示不一致。
- 监控浮窗补充展开/收纳交互，并优化收纳时的横纵联动补间动画。
- WebUI 通用输入框与选择器改为统一标签区和说明区高度，修复因提示文案行数不同导致的参差不齐。

## [1.2.5] - 2026-03-15

### Changed

- 商品详情在窄屏下改为单独详情页展示，保留当前筛选条件并提供返回列表入口，避免移动端抽屉内容过挤。

## [1.2.4] - 2026-03-15

### Changed

- WebUI 适配系统深色模式，统一页面壳层、筛选区、表格操作列和卡片状态的明暗主题表现。
- WebUI 响应式布局断点已对齐，修复导航栏在中间宽度区间切换抽屉后主内容仍按桌面双栏排布的问题。
- 顶部 Banner 调整为与左侧导航留白对齐的悬浮粘性样式，并增强毛玻璃效果，滚动时层次更稳定。

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
