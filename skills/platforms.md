# 技能：多平台（淘宝）使用指南

**场景**：插件已从"闲鱼专用"扩展为多平台。本文说明平台机制、各平台能力差异与淘宝的正确用法，供主 LLM agent 与开发者参考。

## 能力矩阵（当前）

| 能力 | 闲鱼 goofish | 淘宝 taobao |
|---|---|---|
| 订阅监控（建/删/改/停/恢复/立即查） | ✅ | ✅（`platform="taobao"`） |
| 登录（扫码 + 失效自动恢复） | ✅ | ✅（`platform="taobao"`，落地页 login.taobao.com） |
| 推送（降价/上新/建议） | ✅【闲鱼建议】 | ✅【淘宝建议】 |
| 实时搜索 | ✅ `goofish_search_live` | ✅（`platform="taobao"`，关键词+价格过滤，单页） |
| 详情深度分析 | ✅（卖家信用/想要数） | ✅（店铺 DSR/类型 + **SKU 全档真实价**） |
| 收藏 | ✅ | ❌（回复收藏时优雅跳过） |
| 远程 Worker 模式 | ✅ | ❌（仅本地模式） |

## 核心机制（开发者需要知道的三件事）

**1. 平台标签无处不在但默认值安全**
`Subscription`/`NormalizedItem`/`MarketPrice` 都有 `platform` 字段（默认 `goofish`）；数据库唯一键含平台（同一关键词可双平台订阅）；市场均价 EMA 按 `(platform, keyword)` 隔离（闲鱼二手价与淘宝新股价互不污染）。

**2. item_id 前缀防撞号**
闲鱼和淘宝的商品 ID 都是纯数字空间，存储层统一要求新平台 ID 带前缀（`taobao:963892247731`），裸 ID 一律视为闲鱼（兼容存量）。拼商品 URL 只能用 `app/platforms/registry.py` 的 `build_item_url()`。

**3. 登录态按平台隔离**
会话文件与浏览器 profile 均按平台独立：`storage_state.{platform}.json` + `browser_profile_{platform}/`。闲鱼登录**不会**给淘宝域播种 cookie（实测），各扫各的码。淘宝订阅触发 `AUTH_REQUIRED` 时，恢复流程会推送**淘宝**二维码（不是闲鱼的）。

**登录入口（与闲鱼对齐）**：
- 斜杠命令：`/闲鱼 登录 淘宝`（或 `taobao`）手动发起淘宝扫码；`/闲鱼 登录取消`、扫码后回复任意消息确认——这两个对全平台 flow 通用。
- LLM 工具：`goofish_start_login(platform="taobao")` / `goofish_check_login(platform="taobao")`（后者对淘宝走真实登录态探测：探测搜索页并监听 `mtop.user.getusersimple`，已登出不会误报正常）。
- 免扫码自动登录：淘宝曾登录过（storage_state 存在）且持久 profile 里 cookie 仍有效时，发起登录会先探测一次并自动保存，无需扫码（与闲鱼 pre-QR 捷径一致）。
- 登录态查看：`/闲鱼 状态` 逐平台显示登录态保存状态与时间。
- 命令行手动种登录态：`python save_state.py --platform taobao`。

## 淘宝的两个数据真相（使用时必须知道）

**① 列表价 ≠ 到手价（SKU 引流）**
淘宝搜索列表价是 SKU 区间**最低价**——官方旗舰店一个链接里塞 12-23 个档位（RTX 5050 到 5090D），标着 ¥2075 的"5090D"点开发现 5090D 档要 ¥10999。
- 决策卡片会识别"价格异常/混合型号风险"并降权
- 要真实档位价：`goofish_analyze_item_detail` 分析淘宝商品，返回**全档 SKU 价目表**（哪个型号有货、多少钱）

**② 有头浏览器是硬要求**
淘宝风控认浏览器指纹胜过认 cookie：headless 即使带真实登录态也必弹滑块。生产环境保持有头；用户手动关掉浏览器窗口不会致命（自动检测重拉）。

## 典型流程

**订阅淘宝商品**
```
用户：订阅淘宝的 RTX5090 显卡，每天看一次
LLM：goofish_create_subscription(keyword="RTX5090 显卡", platform="taobao", interval_sec=86400)
注意：淘宝间隔有下限（taobao_min_interval_sec，默认 1800s，可配置）
```

**实时搜索淘宝商品**
```
用户：淘宝搜一下 RTX 5060 Ti 显卡
LLM：goofish_search_live(keyword="RTX 5060 Ti 显卡", platform="taobao")
铁律：平台名放 platform 参数，严禁留在 keyword 里（会被原样打进搜索框污染结果）。
淘宝仅支持关键词+价格过滤、单页；个人闲置/新发布/地区过滤是闲鱼特有。
采购决策（buyagent_purchase_decision）会自动解析需求里点名的平台并只搜该平台。
```

**淘宝会话失效**
```
淘宝订阅暂停（AUTH_REQUIRED）→ 系统自动推送淘宝二维码
用户用【手机淘宝 App】扫码 → 回复任意消息 → 订阅自动恢复（只恢复淘宝的，不影响闲鱼）
二维码超时/未收到 → 发送 /闲鱼 登录 淘宝 重新发起（或 goofish_start_login(platform="taobao")）
```

**查淘宝商品真实价格**
```
用户：这个淘宝链接值得买吗 https://item.taobao.com/item.htm?id=...
LLM：goofish_analyze_item_detail(url=...)
     → 店铺类型（旗舰/天猫/C店）+ DSR 评分 + SKU 全档真实价 + 风险提示
```

## 数据流（淘宝链路，与闲鱼的对照）

```
搜索：s.taobao.com/search?q=（SSR 直出 HTML，XHR 只有埋点）
  → DOM 层提取卡片（title 属性/priceInt+priceFloat/店铺/销量）
  → click.simba 广告链接过滤 → item_id 加 taobao: 前缀
  对照闲鱼：XHR JSON 嗅探为主

详情：item.taobao.com / detail.tmall.com（同为 SSR）
  → HTML 内嵌 var b={...} JSON（loaderData.home.data.res）
  → seller（DSR/信用等级/体验分）+ skuBase/skuCore（SKU 全档价）

登录：login.taobao.com 扫码 → mtop.user.getusersimple 接口返回 SUCCESS
  → 会话写 storage_state.taobao.json（探测页=搜索页，落地页≠探测页）
```

## 注意事项

- 淘宝轮询频率保守：默认下限 30 分钟（`taobao_min_interval_sec`），实测有头+低频稳定
- 淘宝收藏/远程模式/分页（第 2 页起）暂不支持，后续版本提供
- 淘宝宝贝无发布时间字段（`publish_time=None`），订阅"上新"判定以首次见到为准
