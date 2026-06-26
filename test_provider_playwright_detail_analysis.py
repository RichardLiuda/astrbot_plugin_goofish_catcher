from __future__ import annotations

import sys
import types
import unittest
from types import SimpleNamespace


astrbot_module = types.ModuleType("astrbot")
astrbot_api_module = types.ModuleType("astrbot.api")
astrbot_api_module.logger = SimpleNamespace(
    warning=lambda *args, **kwargs: None,
    info=lambda *args, **kwargs: None,
    error=lambda *args, **kwargs: None,
    debug=lambda *args, **kwargs: None,
)
sys.modules.setdefault("astrbot", astrbot_module)
sys.modules["astrbot.api"] = astrbot_api_module

if "playwright.async_api" not in sys.modules:
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
    sys.modules["playwright"] = playwright_module
    sys.modules["playwright.async_api"] = async_api_module

from app.provider_playwright import _build_deep_analysis_result, _payload_indicates_captcha
from app.types import NormalizedItem


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


if __name__ == "__main__":
    unittest.main()
