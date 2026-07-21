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
- [ ] 1.2 登录态隔离落地：per-platform storage_state/profile；login_url/auth 标记参数化（GoofishLoginSession 已预留 login_url 注入点）
- [ ] 1.3 详情分析保守版（店铺名/天猫 vs C 店）；favorite_item 先 unsupported
- [ ] 1.4 已知错配修复：角标误当标题、价格拼接爆炸（实证案例见 gotchas.md）

### 阶段 0 剩余（顺延）
- [ ] 0.3b 详情解析入档案：`_build_deep_analysis_result`/`_find_item_detail_payload`/`_classify_credit`/图片提取（~400 行）移入 profile 钩子，provider_playwright 留 re-export 兼容（test_provider_playwright_detail_analysis 护行为）；顺带统一 `_payload_indicates_captcha` 双版本差异（provider 8 标记 vs login_session 3 标记）
- [ ] 0.4 多 provider 容器：build_providers() -> dict[str, SearchProvider]，scheduler 按 sub.platform 路由；单平台行为不变

### 阶段 2：意图引擎 + 决策卡片（核心差异化）
- [ ] 2.1 app/intent/：LLM 拆解（关键词/属性/预算/成色）+ 降级阶梯 Level 0-3（LLM 生成，失败回退整句当关键词）
- [ ] 2.2 asyncio.gather 多平台并发，单平台 10s 超时、失败隔离
- [ ] 2.3 聚合：平台内去重 + 风险标签（闲鱼二手风险词/淘宝 C 店谨慎/天猫旗舰售后优）+ 复用 recommender 排序
- [ ] 2.4 Markdown 决策卡片渲染器，精确匹配为空时顶部 FallbackNotice；输出走现有 MessageChain/Nodes
- [ ] 2.5 新 llm_tool（必须在 main.py）：buyagent_purchase_decision、buyagent_compare；薄 CLI 复用 driver 模式

### 阶段 3（按需）
慢慢买逆向 API + KV 缓存表（URL MD5，TTL 1h，仅服务新品链接）；京东适配器（非 mtop，独立引擎）；多平台订阅 UI；worker 协议加 platform 字段；Admin 平台状态面板；每平台速率限制。

## 明确不做（砍掉的轮子）

跨平台 SKU 去重（不同平台=不同商品）；京东官方 API（要联盟资质，Playwright 路线更现实）；Amazon Keepa（价值最低，最后）；重型独立 CLI（driver 模式已证明可独立跑）。
