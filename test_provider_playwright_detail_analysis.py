from __future__ import annotations

import sys
import types
import unittest
from types import SimpleNamespace


# 真实 astrbot / playwright 可导入时不装桩：直接赋值会顶掉真模块，污染全量
# discover 中后续加载的测试（如 test_reply_favorite）。仅裸环境装桩，且一律
# setdefault。
try:
    import astrbot.api  # noqa: F401
except ImportError:
    astrbot_module = types.ModuleType("astrbot")
    astrbot_api_module = types.ModuleType("astrbot.api")
    astrbot_api_module.logger = SimpleNamespace(
        warning=lambda *args, **kwargs: None,
        info=lambda *args, **kwargs: None,
        error=lambda *args, **kwargs: None,
        debug=lambda *args, **kwargs: None,
    )
    sys.modules.setdefault("astrbot", astrbot_module)
    sys.modules.setdefault("astrbot.api", astrbot_api_module)

try:
    import playwright.async_api  # noqa: F401
except ImportError:
    playwright_module = types.ModuleType("playwright")
    async_api_module = types.ModuleType("playwright.async_api")

    class _Dummy:
        pass

    class _PlaywrightError(Exception):
        pass

    async_api_module.Browser = _Dummy
    async_api_module.BrowserContext = _Dummy
    async_api_module.Playwright = _Dummy
    async_api_module.TimeoutError = TimeoutError
    async_api_module.Error = _PlaywrightError
    async_api_module.async_playwright = lambda: None
    sys.modules.setdefault("playwright", playwright_module)
    sys.modules.setdefault("playwright.async_api", async_api_module)

from app import login_session
from app.platforms.goofish import GOOFISH_PROFILE
from app.platforms.taobao import TAOBAO_PROFILE
from app.provider_agent import normalize_llm_items
from app.provider_playwright import (
    PlaywrightSearchProvider,
    _build_deep_analysis_result,
    _payload_indicates_captcha,
)
from app.types import NormalizedItem, ProviderErrorCode


def _build_provider(profile=None, llm_call=None) -> PlaywrightSearchProvider:
    # __init__ 只读 settings.playwright_executable_path，其余字段按需 stub
    return PlaywrightSearchProvider(
        SimpleNamespace(playwright_executable_path=None),
        profile=profile,
        llm_call=llm_call,
    )


class _FakePage:
    """_classify_timeout_page_state 只读 url / frames / content()。"""

    def __init__(self, url: str, html: str = "<html><body>ok</body></html>") -> None:
        self.url = url
        self.frames = []
        self._html = html

    async def content(self) -> str:
        return self._html

    def locator(self, selector):
        class _Locator:
            async def aria_snapshot(self):
                return '[button] "登录"'

        return _Locator()


class ProviderPlaywrightDetailAnalysisTests(unittest.TestCase):
    def test_detail_analysis_uses_current_item_seller_not_recommendation_user(self) -> None:
        item = NormalizedItem(
            item_id="1054342147837",
            title="尼康Z9",
            price=16200,
            url="https://www.goofish.com/item?id=1054342147837",
        )
        payloads = [
            {
                "api": "mtop.taobao.idle.pc.detail",
                "ret": ["SUCCESS::调用成功"],
                "data": {
                    "itemDO": {
                        "itemId": "1054342147837",
                        "title": "尼康Z9，原电原充",
                        "wantCnt": "17",
                        "browseCnt": "3832",
                    },
                    "sellerDO": {
                        "nick": "安工数码",
                        "sellerId": 2469902406,
                        "newGoodRatioRate": "97%",
                        "hasSoldNumInteger": 184,
                        "userRegDay": 2983,
                        "idleFishCreditTag": {
                            "trackParams": {"sellerLevel": "5"}
                        },
                    },
                },
            },
            {
                "api": "mtop.taobao.idle.item.web.recommend.list",
                "ret": ["SUCCESS::调用成功"],
                "data": {
                    "cardList": [
                        {"cardData": {"user": {"userNick": "错误推荐卖家"}}}
                    ]
                },
            },
        ]

        result = _build_deep_analysis_result(
            item=item,
            payloads=payloads,
            page_title="尼康Z9_闲鱼",
        )

        self.assertEqual(result.seller_name, "安工数码")
        self.assertEqual(result.seller_id, "2469902406")
        self.assertEqual(result.credit_status, "good")
        self.assertIn("好评率97%", result.seller_credit or "")
        self.assertIn("闲鱼信用等级5", result.seller_credit or "")
        self.assertEqual(result.want_count, 17)
        self.assertEqual(result.browse_count, 3832)
        self.assertNotIn("错误推荐卖家", result.summary)

    def test_detail_rgv_validate_response_is_treated_as_captcha(self) -> None:
        self.assertTrue(
            _payload_indicates_captcha(
                {
                    "api": "mtop.taobao.idle.pc.detail",
                    "ret": ["FAIL_SYS_USER_VALIDATE::RGV587_ERROR::SM::哎哟喂,被挤爆啦"],
                }
            )
        )


class GoofishDetailPageTitleTests(unittest.TestCase):
    """parse_detail_page 从 <title> 截取的标题必须反转义（master 用 page.title() 已解码）。"""

    def test_page_title_html_entities_are_unescaped(self) -> None:
        item = NormalizedItem(
            item_id="123",
            title="",
            price=100.0,
            url="https://www.goofish.com/item?id=123",
        )
        html = "<html><head><title>尼康 Z9 &amp; 原厂手柄_闲鱼</title></head></html>"
        result = GOOFISH_PROFILE.parse_detail_page(html, [], item)
        self.assertEqual((result.raw or {}).get("title"), "尼康 Z9 & 原厂手柄")


class NormalizeLlmItemsPlatformTests(unittest.TestCase):
    """normalize_llm_items 的平台上下文：goofish 产物不变，taobao 走前缀方案。"""

    def test_goofish_output_unchanged(self) -> None:
        raw = [
            {"title": "iPhone 15", "price": 4200, "url": "", "item_id": "123"},
            {"title": "相对路径", "price": 10, "url": "/item?id=456"},
        ]
        items = normalize_llm_items(raw, profile=GOOFISH_PROFILE)
        self.assertEqual(items[0].item_id, "123")
        self.assertEqual(items[0].url, "https://www.goofish.com/item?id=123")
        self.assertEqual(items[0].platform, "goofish")
        self.assertEqual(items[1].url, "https://www.goofish.com/item?id=456")
        # 缺省（不传 profile）与 goofish 档案产物一致
        legacy = normalize_llm_items(raw)
        self.assertEqual(
            [(i.item_id, i.url, i.platform) for i in legacy],
            [(i.item_id, i.url, i.platform) for i in items],
        )

    def test_taobao_items_are_prefixed_and_url_built_by_registry(self) -> None:
        raw = [
            {"title": "RTX 5070Ti", "price": 5999, "item_id": "884639892324"},
            {"title": "相对路径", "price": 10, "url": "/item.htm?id=456"},
        ]
        items = normalize_llm_items(raw, profile=TAOBAO_PROFILE)
        self.assertEqual(items[0].item_id, "taobao:884639892324")
        self.assertEqual(items[0].platform, "taobao")
        # URL 兜底走注册表模板，而不是 goofish 的 /item?id=
        self.assertEqual(
            items[0].url, "https://item.taobao.com/item.htm?id=884639892324"
        )
        # 相对路径按淘宝 base_url 归一
        self.assertEqual(items[1].url, "https://www.taobao.com/item.htm?id=456")
        self.assertEqual(items[1].item_id, "taobao:456")


class NormalizeItemCandidatePlatformTests(unittest.TestCase):
    """payload 提取路径 _normalize_item_candidate 的平台前缀化。"""

    def test_goofish_candidate_unchanged(self) -> None:
        provider = _build_provider()
        item = provider._normalize_item_candidate(
            {"title": "尼康Z9", "itemId": "456", "price": 16200}
        )
        assert item is not None
        self.assertEqual(item.item_id, "456")
        self.assertEqual(item.url, "https://www.goofish.com/item?id=456")
        self.assertEqual(item.platform, "goofish")

    def test_taobao_candidate_prefixed(self) -> None:
        provider = _build_provider(profile=TAOBAO_PROFILE)
        item = provider._normalize_item_candidate(
            {"title": "RTX 5070Ti", "itemId": "789", "price": 5999}
        )
        assert item is not None
        self.assertEqual(item.item_id, "taobao:789")
        self.assertEqual(item.platform, "taobao")
        self.assertEqual(item.url, "https://item.taobao.com/item.htm?id=789")


class ProfileUrlPredicateRoutingTests(unittest.IsolatedAsyncioTestCase):
    """引擎 URL 级登录墙判定必须走注入档案的钩子，而非硬编码闲鱼版。"""

    async def test_taobao_login_redirect_detected_with_taobao_profile(self) -> None:
        provider = _build_provider(profile=TAOBAO_PROFILE)
        page = _FakePage("https://login.taobao.com/member/login.jhtml")
        error = await provider._classify_timeout_page_state(page)
        assert error is not None
        self.assertEqual(error.code, ProviderErrorCode.AUTH_REQUIRED)

    async def test_goofish_profile_ignores_taobao_login_url(self) -> None:
        provider = _build_provider()
        page = _FakePage("https://login.taobao.com/member/login.jhtml")
        self.assertIsNone(await provider._classify_timeout_page_state(page))

    async def test_goofish_login_redirect_still_detected(self) -> None:
        provider = _build_provider()
        page = _FakePage("https://passport.goofish.com/mini_login.htm")
        error = await provider._classify_timeout_page_state(page)
        assert error is not None
        self.assertEqual(error.code, ProviderErrorCode.AUTH_REQUIRED)


class LlmLoginCheckGateTests(unittest.IsolatedAsyncioTestCase):
    """LLM 登录判定兜底按档案开关：淘宝访客态必须跳过。"""

    async def test_taobao_profile_skips_llm_login_check(self) -> None:
        calls: list[str] = []

        async def llm_call(prompt: str, system_prompt: str) -> str:
            calls.append(prompt)
            return '{"logged_in": false}'

        provider = _build_provider(profile=TAOBAO_PROFILE, llm_call=llm_call)
        page = _FakePage("https://s.taobao.com/search?q=x")
        self.assertIsNone(await provider._classify_timeout_page_state(page))
        self.assertEqual(calls, [])

    async def test_goofish_profile_still_uses_llm_login_check(self) -> None:
        async def llm_call(prompt: str, system_prompt: str) -> str:
            return '{"logged_in": false}'

        provider = _build_provider(llm_call=llm_call)
        page = _FakePage("https://www.goofish.com/search?q=x")
        error = await provider._classify_timeout_page_state(page)
        assert error is not None
        self.assertEqual(error.code, ProviderErrorCode.AUTH_REQUIRED)


class CheckLoginStateGuardTests(unittest.IsolatedAsyncioTestCase):
    """心跳探测不得拉起浏览器：未初始化或已死时直接返回 error。"""

    async def _assert_no_launch(self, provider: PlaywrightSearchProvider) -> None:
        launches: list[bool] = []

        async def _record_launch():
            # check_login_state 自身会吞 Exception 返回 error，
            # 故用记录而非抛错来断言「未尝试拉起」。
            launches.append(True)
            raise RuntimeError("boom")

        provider._open_operation_context = _record_launch  # type: ignore[method-assign]
        self.assertEqual(await provider.check_login_state(), "error")
        self.assertEqual(launches, [])

    async def test_uninitialised_browser_returns_error(self) -> None:
        await self._assert_no_launch(_build_provider())

    async def test_dead_persistent_context_returns_error(self) -> None:
        provider = _build_provider()
        provider._persistent_context = SimpleNamespace(
            browser=SimpleNamespace(is_connected=lambda: False)
        )
        await self._assert_no_launch(provider)

    async def test_dead_browser_returns_error(self) -> None:
        provider = _build_provider()
        provider._browser = SimpleNamespace(is_connected=lambda: False)
        await self._assert_no_launch(provider)


class ValidateLoginCaptchaScopeTests(unittest.TestCase):
    """validate_login 的验证码判定保持 master 窄口径；搜索路径共享版不受影响。"""

    def test_rate_limit_ret_is_not_captcha_for_login_validation(self) -> None:
        payload = {
            "ret": ["FAIL_SYS_USER_VALIDATE::RGV587_ERROR::SM::哎哟喂,被挤爆啦"]
        }
        self.assertFalse(login_session._payload_indicates_captcha(payload))
        # 同一 payload 在搜索路径的共享 8 标记版下仍判 captcha
        self.assertTrue(_payload_indicates_captcha(payload))

    def test_hard_captcha_markers_still_detected(self) -> None:
        self.assertTrue(
            login_session._payload_indicates_captcha({"ret": ["FAIL::请输入验证码"]})
        )
        self.assertTrue(
            login_session._payload_indicates_captcha({"ret": ["x", "captcha required"]})
        )

    def test_only_first_three_ret_entries_are_scanned(self) -> None:
        payload = {"ret": ["A", "B", "C", "验证码"]}
        self.assertFalse(login_session._payload_indicates_captcha(payload))
        self.assertTrue(_payload_indicates_captcha(payload))


if __name__ == "__main__":
    unittest.main()
