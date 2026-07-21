# 淘宝搜索功能使用指南

> 适用版本：多平台改造阶段 1.1（`feature/modify` 分支，commit `729e727` 起）
> 读者：使用者 + 开发者。每个操作步骤下方附「数据流」说明，开发者可按图索骥。

---

## 1. 这是什么

在原闲鱼插件的抓取引擎上，通过 **SiteProfile 站点档案** 接入的第二个电商平台。

| 能力 | 状态 |
|---|---|
| 淘宝关键词搜索（访客态） | ✅ 已验证 |
| 结构化输出（ID/标题/价格/链接/店铺/销量） | ✅ 已验证 |
| 广告链接过滤（`click.simba.taobao.com`） | ✅ |
| 淘宝独立登录（扫码） | ⏳ 阶段 1.2（当前靠手动过滑块建立会话） |
| 分页（第 2 页起） | ⏳ 未实测，当前仅单页 |
| 商品详情分析（店铺信用/风险） | ⏳ 阶段 1.3 |
| AstrBot 插件内调用（llm_tool） | ⏳ 阶段 2，当前入口是 `scripts/local_lab.py` |

**数据流**：用户命令 → `scripts/local_lab.py` → `PlaywrightSearchProvider(settings, profile=TAOBAO_PROFILE)`
→ 同一套浏览器引擎按淘宝档案执行 → 输出 `list[NormalizedItem]`。
引擎不变，变的只是注入的档案——这是整个多平台改造的核心机制。

---

## 2. 环境准备

```powershell
# 仓库根目录 D:\Laboratory\buy_agent
.venv/Scripts/python.exe -m playwright install chromium   # 首次或浏览器缺失时
```

所有产物（会话、截图、探针快照）写入 `local_data/`（已 gitignore，含 cookie，勿提交）。

**数据流**：`local_lab.py` 复用插件自身的 `app.login_session.GoofishLoginSession` 与
`app.provider_playwright.PlaywrightSearchProvider`——跑的就是生产代码路径，不是仿制品。
配置由 `_make_settings()` 构造 `PluginSettings`（`app/config.py`），
`playwright_storage_state_path` 指向 `local_data/` 下的会话文件，
`playwright_user_data_dir=None`（两者互斥，见 .kimi/gotchas.md）。

---

## 3. 使用流程

### 3.1 建立淘宝会话（首次或会话失效时）

```powershell
.venv/Scripts/python.exe scripts/local_lab.py sso "RTX 5090"
```

1. 弹出有头浏览器打开淘宝搜索页；新浏览器指纹通常会弹**滑块验证**
2. **你在窗口里手动过滑块**（或选择登录淘宝账号，皆可）
3. 脚本每 3 秒自动检测一次——**页面上出现商品列表即自动继续**，无需回终端操作
4. 会话自动保存到 `local_data/storage_state.taobao.json`

> 判断"验证已通过"为什么看商品数量而不是页面文字：滑块相关的 HTML 标记
> （"滑块"/"验证码"等）在验证通过后仍残留在页面源码里，会误判；
> 能提取到 ≥3 条商品才是真的通了（轮询上限 6 分钟）。

**数据流**：
```
sso 命令 → PlaywrightSearchProvider（闲鱼档案，仅借用其浏览器与提取骨架）
  → 注入 local_data/storage_state.taobao.json（若存在，否则全新访客指纹）
  → 访问 s.taobao.com/search?q= → 命中风控 → 用户手动过滑块
  → 轮询：_extract_items_from_payloads / _extract_items_from_dom ≥3 条 → 放行
  → context.storage_state() 原子落盘 storage_state.taobao.json
      （含阿里风控信任 cookie：x5sec 等 + 各域会话 cookie）
```

### 3.2 搜索淘宝

```powershell
.venv/Scripts/python.exe scripts/local_lab.py search-taobao "RTX 5090"
# 加 --headless 可无头运行（但无头极易被风控，仅调试用）
```

输出示例：

```
[TAOBAO] keyword='RTX 5090' pages=1 → 39 items
  [taobao:963086395990] ¥23666.96   '技嘉RTX5090 D V2显卡 魔鹰雪鹰…'
    店铺=技嘉旗舰店  销量=100+人付款
    https://detail.tmall.com/item.htm?id=963086395990&…
```

**数据流**（TaobaoProfile 的完整链路，也是本功能的精华）：

```
关键词
  → TAOBAO_PROFILE.build_search_url(keyword)            # app/platforms/taobao.py
      "https://s.taobao.com/search?q=RTX%205090"
  → 引擎 Chromium 打开页面（注入 storage_state.taobao.json 的 cookie）
      淘宝是 SSR 页面：商品直出在 HTML，XHR 只有埋点 → 一级 payload 嗅探恒空
  → 二级 DOM 提取：page.eval_on_selector_all(
        profile.dom_card_link_selector,                  # "a[href*='item.htm']"
        profile.dom_card_extractor_js)                   # 按淘宝卡片结构取字段
      标题  ← div[class*='title--'] 的 title 属性（关键词高亮把标题拆成多段，
                                                 取属性值最稳）
      价格  ← div[class*='priceInt--'] + div[class*='priceFloat--'] 拼接
      店铺  ← span[class*='shopNameText--']
      销量  ← span[class*='realSales--']
  → profile.parse_dom_card(card) 逐卡解析：
      host 白名单（item.taobao.com / detail.tmall.com）过滤 click.simba 广告
      → registry.extract_item_id_from_url 取原始数字 ID
      → registry.make_item_id("taobao", raw_id) 加前缀 → "taobao:963086395990"
      → NormalizedItem(raw={shopName, salesText, priceDesc})
  → 引擎去重（item_id 集合）→ list[NormalizedItem] 打印
```

### 3.3 会话的日常复用与失效处理

- 之后每次 `search-taobao` 自动加载 `storage_state.taobao.json`，**通常不再需要过滑块**
- 若再次返回 `CAPTCHA` / `AUTH_REQUIRED` / 0 条结果：重跑 3.1 的 `sso` 命令刷新会话
- 闲鱼会话与淘宝会话**文件隔离**：`storage_state.json` ↔ `storage_state.taobao.json`，
  互不影响（SSO 实验已证实闲鱼登录不会给淘宝域播种 cookie，这是有意设计）

**数据流**：会话文件 → `PluginSettings.playwright_storage_state_path` → 每次操作
`browser.new_context(storage_state=…)` 注入 cookie；操作成功后引擎
`_persist_context_storage_state()` 回写最新 cookie（自动续期，无独立保活任务）。

---

## 4. 输出字段说明（NormalizedItem）

| 字段 | 淘宝取值 | 说明 |
|---|---|---|
| `item_id` | `taobao:963086395990` | **必须带平台前缀**：淘宝与闲鱼 ID 同为纯数字空间，前缀防撞号；规则见 `app/platforms/registry.py`（裸 ID 一律视为闲鱼，兼容存量数据） |
| `title` | 完整商品标题 | 取自卡片 title 属性（非高亮碎片拼接） |
| `price` | `23666.96` | priceInt+priceFloat 拼接。**注意：列表价是 SKU 区间最低价**，存在低价引流（如 ¥2768 的"5090D"实为低档 SKU），比价/聚合层需知悉 |
| `url` | `item.taobao.com` / `detail.tmall.com` 链接 | 天猫店商品走 tmall 域名，均为真实详情页 |
| `platform` | `"taobao"` | 0.1 起 NormalizedItem 自带平台标签 |
| `raw.shopName` | `技嘉旗舰店` | 风险分层素材：旗舰店/天猫 vs 淘宝店 |
| `raw.salesText` | `100+人付款` | 热度参考 |
| `raw.priceDesc` | `优惠后` | 价格口径标记 |
| `publish_time` | `None` | 淘宝搜索页无发布时间 |

---

## 5. 故障排查

| 症状 | 原因与处理 |
|---|---|
| `CAPTCHA: captcha detected on 淘宝 page` | 指纹被风控。重跑 `sso` 手动过滑块刷新会话；降低调用频率；避免 `--headless` |
| `AUTH_REQUIRED` 但页面明明有商品 | 1.1 已修复（阿里登录组件误报），确认代码已更新到 `729e727` 之后 |
| 0 条结果且无报错 | 会话半失效。重跑 `sso`；检查是否用了 `--headless` |
| 价格异常（¥24、¥509032） | 1.1 已修复（那是旧通用解析器的角标误匹配/拼接爆炸），确认走 `search-taobao` 而非 `sso` 的输出做判断 |
| 结果里混着"广告感"很强的链接 | 不应出现。`click.simba.taobao.com` 已双重过滤，若复现请检查 `taobao.py` 的 `_ITEM_HOST_RE` |
| 第 2 页报错 | 预期内：淘宝分页选择器未实测（pending），当前仅单页 |

---

## 6. 开发者：如何接入第三个平台（以京东为例）

1. **实测侦察**（先不写代码）：用 `sso` 同款探针思路访问目标站搜索页，回答四个问题——
   数据在 XHR 还是 DOM？卡片选择器与字段结构？登录墙/风控特征？访客可否搜索？
2. 新建 `app/platforms/<platform>.py`，填 `SiteProfile`（`app/platforms/base.py`）：
   - 数据字段：搜索 URL、登录标记、选择器组
   - 钩子函数：`build_search_url` / `is_auth_url` / `is_captcha_url` / `normalize_item_page_title`
   - 若卡片结构与闲鱼差异大：加 `parse_dom_card` + `dom_card_extractor_js`（参照 taobao.py）
3. `registry.py` 注册平台：URL 模板、显示名、`make_item_id` 前缀
4. 写 `test_<platform>_profile.py`（参照 test_taobao_profile.py：合成卡片 dict 测解析，
   不依赖浏览器）
5. 真实搜索验证 + 更新 .kimi/ 三份文档 + CHANGELOG

**数据流**：引擎（`provider_playwright.py`）所有平台特数据的读取点都已收口到
`self._profile.<field>`——新平台**不需要**改引擎，只交一份档案。

---

## 7. 全景数据流图

```
用户命令 local_lab.py
   │
   ├─ login/check/search ────────→ profile=GOOFISH_PROFILE（默认）
   │                                 → goofish.com（XHR 嗅探为主）
   ├─ search-taobao ─────────────→ profile=TAOBAO_PROFILE
   │                                 → s.taobao.com（SSR → DOM 定制钩子）
   └─ sso ───────────────────────→ 建立/刷新 storage_state.taobao.json
                                         │
共享底座：Playwright 浏览器管理 · storage_state 注入/回写 ·
          三级提取（payload→DOM→AX+LLM）· 错误分类（AUTH/CAPTCHA/RATE_LIMITED）·
          registry（item_id 前缀 · build_item_url）
```

相关文档：[.kimi/architecture.md](.kimi/architecture.md)（模块地图）、
[.kimi/gotchas.md](.kimi/gotchas.md)（实战坑）、[.kimi/roadmap.md](.kimi/roadmap.md)（改造进度）。
