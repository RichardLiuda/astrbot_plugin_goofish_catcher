# 开发注意事项（动手前必看）

## 抓取实战坑（部分源自 .claude/skills/run-goofish-scraper/SKILL.md，已本地实证）

- **headless 连续快跑会被闲鱼限流**（约 3 次请求后 ERR_CONNECTION_RESET 或 0 结果）。本地实证：5 次 headless 页面加载后搜索返回 0 条，换有头立即恢复 30 条。**生产配置硬编码有头**（config.py:353 playwright_headless=False）。测试间隔 30-60s。
- `check_login_state()` 在浏览器/context 未打开时直接返回 'error'——必须先开 context（driver 模式）。
- `playwright_storage_state_path` 与 `playwright_user_data_dir` **互斥**：前者=每次新建 context 注入 cookie；后者=持久 profile（生产默认，指纹持续累积，更抗风控）。
- 搜索页 0 items + payloads=3 → 会话过期（那 3 个 payload 是问卷配置）。
- mtop 接口常常**滚动页面后才触发**，裸 goto + wait 可能拿不到 payload。
- `playwright_block_assets=True` 理论上可能误拦懒加载内容，排查 0 结果时先关掉试。
- 登录校验（validate_login）硬性要求 `mtop.taobao.idlemessage.pc.loginuser.get` 和 `mtop.idle.web.user.page.nav` 两个接口出现成功响应。
- **`payloads=3 + 0 items` 有两种病因**（实证）：①会话过期；②headless 被限流导致搜索 XHR 根本没发出（此时 check 仍可能 ok——首页不要求登录）。鉴别：跑 check + 有头 search。
- 闲鱼会话寿命观察：扫码登录后约 29 小时过期（期间有多次 headless 限流运行，可能加速）。
- `_payload_indicates_captcha` 存在**两个版本**（0.3b 待统一）：provider 版 8 个标记（含 rgv587/punish/baxia），login_session 版 3 个标记——行为差异是有意保留的，统一前不要只改一边。

## 淘宝实验结论（2026-07-20 本地实证，产物在 local_data/）

- 淘宝搜索是 **SSR 页面**：XHR 只有埋点/监控（arms/ICE），商品数据在 DOM 里 → **提取主路径 = DOM 层**（闲鱼是 XHR 层），TaobaoProfile 必须自定义卡片选择器与字段规则。
- 闲鱼登录**不会**给 .taobao.com 域播种 cookie（cookie2=False）→ 登录态按平台隔离（已定决策）。
- 淘宝允许**访客搜索**，但新浏览器指纹必弹滑块；手动过后页面正常。
- 闲鱼式 DOM 提取直接套淘宝会错配：标题抓成角标（"品牌旗舰店/分期免息"）、价格误匹配（¥24.00 / ¥5080 万拼接爆炸）、混入 `click.simba.taobao.com` 广告链接——这些都要在 TaobaoProfile 里解决。
- 实验脚本：`scripts/local_lab.py {login|check|search|search-taobao|sso}`，产物在 `local_data/`（含 cookie，已 gitignore）。日志级别 `LAB_LOG=INFO`。

## 淘宝适配实战经验（2026-07-21，1.1 落地验证）

- 淘宝访客/半登录态页面常驻阿里登录组件：embedded_login_markers 含 "alibaba-login-box" 会**误报 AUTH_REQUIRED**（且先于 captcha 检查执行），TAOBAO_PROFILE 该字段必须为空，只认 login.taobao.com 重定向。
- "滑块/验证码"等 HTML 标记在**验证通过后仍残留在页面源码里**——判断验证是否已通过不能用 HTML 标记，要用"能否提取到 ≥3 条商品"（sso 探针的轮询逻辑就是这么做的）。
- 淘宝风控惩罚页走 `cf.aliyun.com/nocaptcha/initialize.jsonp`，被惩罚的 mtop 接口是 `mtop.alibaba.fc.api.maoxland.*`——说明淘宝搜索**也会发 mtop XHR**，未惩罚时 payload 层可能有货（后续可研究）。
- 淘宝列表价是 SKU 区间最低价，存在低价引流（如 ¥2768 的"5090D"实为 5070Ti 档位）——列表价≠真实到手价，聚合/比价层必须知道这一点。
- `sso` 探针命令的 provider 用的是**闲鱼档案**（历史原因），其提取结果不代表 TaobaoProfile；淘宝提取以 `search-taobao` 为准。

## AstrBot 插件机制红线

- **所有 @llm_tool 必须定义在 main.py**（AstrBot 校验 `handler.__module__ == metadata.module_path`），新工具也不例外。
- llm 工具里发消息用 `context.send_message(umo, chain)` 旁路；工具返回值只给 LLM 看。
- 配置项四同步：` _conf_schema.json` / `app/_admin_schema.json` / `admin_service.py`（_settings_to_editable_values + _config_groups）/ `config.py`。overlay（admin_runtime_config.json）永远覆盖 AstrBot 面板同名项。
- 前端是 Preact+htm+MUI 预打包 bundle：改 `data/admin_webui/` 源码后必须 `npm run build:webui`。

## 测试基线

- 仓库**没装 pytest**，用 unittest：`.venv/Scripts/python.exe -m unittest <模块名>`。
- 测试文件头部需要 astrbot stub 前置块（照抄 test_reply_favorite.py）；test_remote_auth_flow 单独跑会 import 失败（依赖别的测试文件先注入 stub）。
- **既有失败基线**：4 文件连跑 = "Ran 51 tests, FAILED (errors=4)"，4 个错误都在 test_remote_auth_flow（MessageChain stub 过时），与改造无关。改完后基线不得恶化。

## 发版流程（.claude/skills/release/SKILL.md）

CHANGELOG（顶部插入新版本块）→ metadata.yaml 版本号 → commit → tag → `gh release create`。
**动了 worker_server.py 就必须更新"Worker ≥ vX.Y.Z"兼容行**并加警告引用块；没动就不变。
大改动随手在 CHANGELOG 的 Unreleased/新版本块记 ### Added/Changed/Fixed。

## Git 纪律

- 不主动 commit/push，需用户确认；`local_data/`（cookie）已 gitignore，严禁提交。
- 改完代码扫一遍注释/docstring 是否描述旧行为，一并更新。
