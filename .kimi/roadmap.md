# 多平台改造 Roadmap

目标：闲鱼订阅监控插件 → 多平台采购决策 Agent（自然语言 → 意图拆解 → 多平台并发搜索 → 聚合比价/历史价 → 降级建议 → 采购决策卡片）。**淘宝优先**（与闲鱼同阿里系）。

## 已定决策（用户拍板）

1. **item_id 前缀化**：适配器产出 `{platform}:{raw_id}`（如 `tb:123`），detector/recommender 当不透明字符串零侵入。
2. **登录态按平台隔离**：独立 storage_state.{platform}.json + browser_profile_{platform}/（SSO 实验已证实闲鱼不播种淘宝域 cookie）。
3. **远程 worker 多平台推迟**：MVP 期间 remote_rest 模式下非闲鱼平台直接报"暂不支持"。
4. **慢慢买历史价移出 MVP**：闲鱼场景现有 price_history + market EMA 已够用；慢慢买只对淘宝/京东新品有意义，阶段 3 再做。

## 核心架构判断（侦察结论）

- 项目是「真实浏览器渲染 + XHR/DOM 嗅探」，**无 MTOP 签名代码**——签名由页面内阿里 SDK 自动完成，新平台不需要造签名轮子。
- 不复制 2500 行 provider per 平台：拆 **通用引擎 + 每平台 SiteProfile**（URL/选择器/auth 标记/payload API 名/字段别名）。
- `SearchProvider` Protocol（app/provider.py:13）就是平台适配器接口；`provider_mode`（local/remote）是部署维度，与平台维度正交。
- 单平台假设雷区：item_id 全局裸用（main.py:1680 拼 goofish URL）、subscriptions 旧唯一键 (umo, keyword)、market_price 按 keyword、登录单槽位、文案硬编码"闲鱼"。

## 阶段拆解与进度

### 阶段 0：平台维度植入（不动抓取逻辑）
- [x] 0.0 侦察：项目跑通 + SSO 实验（2026-07-20，结论见 gotchas.md）
- [x] 0.1 数据模型（2026-07-20 完成）：types.py 三 dataclass 加 platform + DEFAULT_PLATFORM；storage migration v7（subscriptions 加 platform + 唯一键重建 (umo, platform, keyword)；market_price 重建为 (platform, keyword) PK）；scheduler 传 sub.platform；test_storage_platform.py 4 用例全绿，基线 51/4 未恶化
- [x] 0.2 item_id 前缀化（2026-07-20 完成）：`app/platforms/registry.py` 建立——规则=裸 ID 视为 goofish（兼容存量，零数据迁移）、新平台必须带 `{platform}:` 前缀（make_item_id）；`build_item_url` 成为拼商品 URL 唯一收口，main.py:1680 已接入；test_platform_registry.py 16 用例全绿
- [x] 0.3a 引擎/档案拆分（2026-07-21 完成）：`app/platforms/base.py`（SiteProfile：21 数据字段 + 4 钩子）+ `goofish.py`（GOOFISH_PROFILE，钩子逐字搬自原实现）；`PlaywrightSearchProvider` 加可选 profile 注入，BASE_URL 类属性及 4 个模块常量删除改读档案；login_session 重复常量收敛为档案别名。验证：基线 51/4 + 新 20 全绿、行为等价抽查、A/B 测试排除重构嫌疑（AUTH_REQUIRED 系会话自然过期）、重登后有头真实搜索回归通过
### 阶段 1：淘宝适配器（提前于 0.3b/0.4 执行——用第二个平台验证 SiteProfile 抽象）
- [x] 1.1 TaobaoProfile（2026-07-21 完成）：`app/platforms/taobao.py`——s.taobao.com 搜索 URL、`a[href*='item.htm']` 卡片选择器、DOM 字段规则（title 属性取标题/priceInt+priceFloat 拼价格/shopName/realSales 进 raw）、host 白名单过滤 click.simba 广告；引擎新增 `parse_dom_card`/`dom_card_extractor_js` 可选钩子（base.py）；`extract_item_id_from_url`/`normalize_url` 下沉 registry；淘宝 `embedded_login_markers=()`（阿里登录组件常驻页面会误报，只认 login.taobao.com 重定向）；local_lab `search-taobao` 实测 39+ 条正确结果（ID 带前缀、价格/标题/店铺全部正确）。已知遗留：分页选择器未实测（仅单页）、价格 URL 参数名未验证（内存过滤兜底）、SKU 低价引流导致列表价≠真实 SKU 价（聚合层处理）
- [x] 1.2 登录态隔离落地（2026-07-22/23 完成，即 P0）：登录链路三层（GoofishLoginSession/LocalAuthSessionController/RemoteAuthRecoveryCoordinator）全部 profile 化；淘宝登录落地页 login.taobao.com + 校验接口 mtop.user.getusersimple；恢复流程按平台分 flow、只恢复同平台订阅；start_login/check_login 工具加 platform 参数；quick-login 误判根治（quick_login_enabled=False）；local_lab `login-taobao`。15 新测试全绿，总 109 测试/1 既有错误
- [x] 1.3 详情分析（2026-07-23 完成，超出保守版）：实测淘宝详情页为 SSR（无详情 mtop 接口），`SiteProfile.parse_detail_page` 钩子解析 HTML 内嵌 `var b={...}` JSON——店铺三件套（sellerNick/DSR/体验分/店铺类型）、SKU 全档真实价目表（含无货标注，低价引流无处遁形）、主图、信用规则与风险提示；supports_item_detail=True；test_taobao_detail.py 31 用例全绿 + 双真实链接实测通过（天猫 12 档 ¥2399~11999 / C店 23 档 ¥18000~32500）。favorite_item 仍 unsupported（后续单独做）
- [ ] 1.4 已知错配修复：角标误当标题、价格拼接爆炸（实证案例见 gotchas.md）

### 阶段 1.5：淘宝订阅接入插件（0.4 提前，2026-07-21 完成）
- [x] 1.5a watch-taobao CLI 轮询实验：复用 SubscriptionStorage + detector，验证 items/price_history/market_price 带 platform=taobao 落库正确
- [x] 1.5b 插件内淘宝订阅：`build_providers()` 平台路由表（淘宝独立 storage_state/profile 目录，远程模式跳过）；scheduler 按 sub.platform 路由（无 provider 时 PLATFORM_UNAVAILABLE 暂停+告警）；深度分析按 item_id 前缀路由 + `supports_item_detail=False` 短路；`goofish_create_subscription` 加 platform 参数；admin 校验（未启用报错/间隔≥1800s/平台不可改）；通知文案按平台显示名（【淘宝建议】）；淘宝收藏优雅跳过；`taobao_enabled` 配置四同步。9 个路由测试全绿

### 阶段 0 剩余（顺延）
- [ ] 0.3b 详情解析入档案：`_build_deep_analysis_result`/`_find_item_detail_payload`/`_classify_credit`/图片提取（~400 行）移入 profile 钩子，provider_playwright 留 re-export 兼容（test_provider_playwright_detail_analysis 护行为）；顺带统一 `_payload_indicates_captcha` 双版本差异（provider 8 标记 vs login_session 3 标记）
- [x] 0.4 多 provider 容器（随 1.5b 完成）：build_providers() -> dict[str, SearchProvider]，scheduler 按 sub.platform 路由；单平台行为不变

### 阶段 2：意图引擎 + 决策卡片（核心差异化，2026-07-23 完成）
- [x] 2.1 `app/intent/engine.py`：LLM 拆解（关键词/属性/预算/成色/降级阶梯 L0-3，失败回退启发式：整句关键词+锚定预算正则）
- [x] 2.2 并发聚合：`PurchaseDecisionService`（app/purchase.py）——asyncio.gather 打 providers 字典，单平台 20s 超时+异常隔离，空结果逐级降级重搜
- [x] 2.3 `app/aggregator/aggregate.py`：平台内去重 + 风险标签（闲鱼二手词/淘宝旗舰 vs C店）+ LLM/启发式排序（宁缺毋滥）
- [x] 2.4 `app/reporter/card.py`：Markdown 决策卡片，降级提示+💡替代建议+"N 条未进推荐"平台露面+失败平台节
- [x] 2.5 `buyagent_purchase_decision` llm_tool（main.py，第 18 个工具）+ local_lab `decide` 命令（LAB_LLM_* 接任意 OpenAI 兼容 LLM，无配置走启发式）；test_purchase_decision.py 31 用例全绿；lab 实测双平台卡片（66 候选→top5 淘宝+闲鱼另有 30 条露面）

### 阶段 3（按需）
慢慢买逆向 API + KV 缓存表（URL MD5，TTL 1h，仅服务新品链接）；京东适配器（非 mtop，独立引擎）；多平台订阅 UI；worker 协议加 platform 字段；Admin 平台状态面板；每平台速率限制。

## 明确不做（砍掉的轮子）

跨平台 SKU 去重（不同平台=不同商品）；京东官方 API（要联盟资质，Playwright 路线更现实）；Amazon Keepa（价值最低，最后）；重型独立 CLI（driver 模式已证明可独立跑）。
