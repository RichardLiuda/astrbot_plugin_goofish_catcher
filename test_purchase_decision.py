"""2.x 核心管线测试：意图引擎 / 聚合 / 决策卡片 / 编排服务。

llm_call、providers、storage 全部注入 fake，不碰浏览器与网络；
provider 异常与超时用 asyncio.sleep + 短超时模拟。
"""

from __future__ import annotations

import asyncio
import json
import unittest

from app.aggregator.aggregate import (
    DecisionItem,
    dedupe_items,
    rank_items,
    risk_tags_for,
    score_heuristic,
)
from app.intent.engine import PurchaseIntent, parse_intent
from app.platforms.registry import PLATFORM_GOOFISH, PLATFORM_TAOBAO
from app.purchase import PurchaseDecisionService
from app.reporter.card import render_decision_card
from app.types import MarketPrice, NormalizedItem


# ── fakes ────────────────────────────────────────────────────────────────────

class FakeProvider:
    """按关键词返回预设结果；可注入异常或延迟（模拟卡死）。"""

    def __init__(self, results=None, *, error: Exception | None = None, delay_sec: float = 0.0):
        self._results = results or {}
        self._error = error
        self._delay_sec = delay_sec
        self.calls: list[str] = []

    async def search(
        self,
        *,
        keyword: str,
        pages: int,
        timeout_sec: int,
        filters=None,
        price_lower=None,
        price_upper=None,
    ) -> list[NormalizedItem]:
        self.calls.append(keyword)
        if self._delay_sec:
            await asyncio.sleep(self._delay_sec)
        if self._error is not None:
            raise self._error
        return list(self._results.get(keyword, []))


class FakeStorage:
    def __init__(self, prices=None, *, error: Exception | None = None):
        self._prices = prices or {}  # (keyword, platform) -> ema
        self._error = error

    async def get_market_price(self, keyword: str, platform: str = PLATFORM_GOOFISH):
        if self._error is not None:
            raise self._error
        ema = self._prices.get((keyword, platform))
        if ema is None:
            return None
        return MarketPrice(
            keyword=keyword, ema_price=ema, sample_count=3, updated_at=0, platform=platform
        )


def make_llm(payload) -> object:
    """返回固定 JSON 的 fake llm_call。"""

    async def _call(prompt: str, system_prompt: str) -> str:
        return json.dumps(payload, ensure_ascii=False)

    return _call


async def garbage_llm(prompt: str, system_prompt: str) -> str:
    return "抱歉，我无法理解这个需求。"


def make_item(
    item_id: str = "1",
    title: str = "商品",
    price: float = 100.0,
    platform: str = PLATFORM_GOOFISH,
    raw: dict | None = None,
) -> NormalizedItem:
    return NormalizedItem(
        item_id=item_id,
        title=title,
        price=price,
        url=f"https://example.com/item?id={item_id}",
        publish_time=None,
        raw=raw,
        platform=platform,
    )


INTENT_LLM_PAYLOAD = {
    "keyword": "RTX5090",
    "attributes": {"颜色": "红色"},
    "budget_max": 15000,
    "condition": "不限",
    "degradation": [
        {
            "level": 0,
            "keyword": "红色RTX5090",
            "note": "精确匹配颜色",
            "require_terms": ["红色"],
        },
        {"level": 1, "keyword": "RTX5090", "note": "放宽颜色限制"},
        {
            "level": 2,
            "keyword": "RTX5090 显卡",
            "note": "妥协成色",
            "hint": "可考虑黑色+RGB调红",
        },
    ],
}


# ── ① parse_intent 启发式兜底 ────────────────────────────────────────────────

class ParseIntentHeuristicTest(unittest.IsolatedAsyncioTestCase):
    async def test_heuristic_budget_wan_notations(self) -> None:
        for text, expected in (
            ("想买红色RTX5090显卡，预算1万5", 15000.0),
            ("RTX5090，1.5万以内", 15000.0),
            ("RTX5090 预算1w5", 15000.0),
            ("RTX5090，2万以下", 20000.0),
        ):
            intent = await parse_intent(text, llm_call=None)
            self.assertEqual(intent.budget_max, expected, text)

    async def test_heuristic_plain_number_ignores_model_digits(self) -> None:
        # "RTX5090" 里的 5090 不能被当成预算，真正的预算在后文。
        intent = await parse_intent("RTX5090显卡，预算15000元", llm_call=None)
        self.assertEqual(intent.budget_max, 15000.0)

    async def test_heuristic_spaced_model_number_is_not_budget(self) -> None:
        # 回归：空格隔开的型号数字（"RTX 5090 显卡"）不能被误吞为预算——
        # 纯数字必须带预算上下文（预算/以内/元等锚点）才作数。
        intent = await parse_intent("RTX 5090 显卡", llm_call=None)
        self.assertIsNone(intent.budget_max)
        intent = await parse_intent("红色 RTX 5090，8000元以内", llm_call=None)
        self.assertEqual(intent.budget_max, 8000.0)

    async def test_heuristic_levels_and_attributes(self) -> None:
        intent = await parse_intent("想买红色RTX5090显卡，预算1万5", llm_call=None)
        self.assertEqual(intent.raw_query, "想买红色RTX5090显卡，预算1万5")
        self.assertEqual(intent.keyword, "想买红色RTX5090显卡，预算1万5")  # 整句
        self.assertEqual(intent.attributes, {"颜色": "红色"})
        self.assertGreaterEqual(len(intent.degradation), 2)
        l0, l1 = intent.degradation[0], intent.degradation[1]
        self.assertEqual(l0.level, 0)
        self.assertIn("红色", l0.require_terms)
        self.assertNotIn("红色", l1.keyword)

    async def test_heuristic_always_has_level(self) -> None:
        intent = await parse_intent("RTX5090", llm_call=None)
        self.assertGreaterEqual(len(intent.degradation), 1)
        self.assertEqual(intent.degradation[0].keyword, "RTX5090")
        self.assertIsNone(intent.budget_max)
        self.assertEqual(intent.attributes, {})


# ── ② mock llm_call 合法 / 烂 JSON ──────────────────────────────────────────

class ParseIntentLlmTest(unittest.IsolatedAsyncioTestCase):
    async def test_llm_valid_json(self) -> None:
        intent = await parse_intent(
            "想买红色RTX5090，预算1万5", llm_call=make_llm(INTENT_LLM_PAYLOAD)
        )
        self.assertEqual(intent.keyword, "RTX5090")
        self.assertEqual(intent.attributes, {"颜色": "红色"})
        self.assertEqual(intent.budget_max, 15000.0)
        self.assertEqual(intent.condition, "不限")
        self.assertEqual([lv.level for lv in intent.degradation], [0, 1, 2])
        self.assertEqual(intent.degradation[0].require_terms, ("红色",))
        self.assertEqual(intent.degradation[2].hint, "可考虑黑色+RGB调红")

    async def test_llm_fenced_json(self) -> None:
        async def fenced(prompt: str, system_prompt: str) -> str:
            return "```json\n" + json.dumps(INTENT_LLM_PAYLOAD, ensure_ascii=False) + "\n```"

        intent = await parse_intent("红色RTX5090", llm_call=fenced)
        self.assertEqual(intent.keyword, "RTX5090")
        self.assertEqual(len(intent.degradation), 3)

    async def test_llm_garbage_falls_back_to_heuristic(self) -> None:
        intent = await parse_intent("红色RTX5090，预算1万5", llm_call=garbage_llm)
        # 回退启发式：整句 keyword + 正则预算。
        self.assertEqual(intent.keyword, "红色RTX5090，预算1万5")
        self.assertEqual(intent.budget_max, 15000.0)
        self.assertGreaterEqual(len(intent.degradation), 1)

    async def test_llm_exception_falls_back(self) -> None:
        async def boom(prompt: str, system_prompt: str) -> str:
            raise RuntimeError("llm down")

        intent = await parse_intent("RTX5090 预算15000", llm_call=boom)
        self.assertEqual(intent.budget_max, 15000.0)

    async def test_llm_timeout_falls_back(self) -> None:
        async def slow(prompt: str, system_prompt: str) -> str:
            await asyncio.sleep(5)
            return "{}"

        intent = await parse_intent("RTX5090 预算15000", llm_call=slow, timeout_sec=1)
        self.assertEqual(intent.budget_max, 15000.0)


# ── ③ 降级循环 / ④ require_terms / 预算过滤 ──────────────────────────────────

class PurchaseServiceDegradationTest(unittest.IsolatedAsyncioTestCase):
    async def test_degrade_to_l1_when_l0_empty(self) -> None:
        l1_item = make_item("g1", "RTX5090 显卡 全新", 12999.0)
        providers = {
            PLATFORM_GOOFISH: FakeProvider({"红色RTX5090": [], "RTX5090": [l1_item]}),
            PLATFORM_TAOBAO: FakeProvider({}),
        }
        service = PurchaseDecisionService(
            providers=providers, llm_call=make_llm(INTENT_LLM_PAYLOAD)
        )
        report = await service.run("想买红色RTX5090，预算1万5")
        self.assertEqual(report.level_used, 1)
        self.assertEqual(report.level_note, "放宽颜色限制")
        self.assertEqual(len(report.items), 1)
        self.assertEqual(report.searched_platforms, [PLATFORM_GOOFISH, PLATFORM_TAOBAO])
        self.assertEqual(report.errors, {})
        # L0/L1 都搜过
        self.assertEqual(
            providers[PLATFORM_GOOFISH].calls, ["红色RTX5090", "RTX5090"]
        )

    async def test_require_terms_filter_triggers_degradation(self) -> None:
        # L0 有货但标题不含"红色" → 被 require_terms 滤掉 → 降级到 L1 命中。
        black_item = make_item("g2", "RTX5090 显卡 黑色", 11999.0)
        providers = {
            PLATFORM_GOOFISH: FakeProvider(
                {"红色RTX5090": [black_item], "RTX5090": [black_item]}
            ),
        }
        service = PurchaseDecisionService(
            providers=providers, llm_call=make_llm(INTENT_LLM_PAYLOAD)
        )
        report = await service.run("想买红色RTX5090")
        self.assertEqual(report.level_used, 1)
        self.assertEqual(len(report.items), 1)
        self.assertEqual(report.items[0].item.item_id, "g2")

    async def test_all_levels_empty(self) -> None:
        providers = {PLATFORM_GOOFISH: FakeProvider({})}
        service = PurchaseDecisionService(providers=providers, llm_call=None)
        report = await service.run("红色RTX5090")
        self.assertEqual(report.items, [])
        self.assertEqual(report.level_used, 1)  # 停在最后一级
        self.assertIn("均无符合条件", report.summary)
        self.assertFalse(report.used_llm)

    async def test_budget_filter(self) -> None:
        expensive = make_item("g3", "RTX5090 显卡", 18000.0)
        # 启发式 L0 用整句作关键词，fake provider 按整句给货。
        providers = {
            PLATFORM_GOOFISH: FakeProvider({"RTX5090 预算1万5": [expensive]})
        }
        service = PurchaseDecisionService(providers=providers, llm_call=None)
        report = await service.run("RTX5090 预算1万5")
        self.assertEqual(report.intent.budget_max, 15000.0)
        self.assertEqual(report.items, [])  # 18000 > 15000 被过滤

    async def test_market_refs_and_price_note(self) -> None:
        item = make_item("g4", "RTX5090 显卡", 8000.0)
        providers = {PLATFORM_GOOFISH: FakeProvider({"RTX5090": [item]})}
        storage = FakeStorage({("RTX5090", PLATFORM_GOOFISH): 10000.0})
        service = PurchaseDecisionService(
            providers=providers, storage=storage, llm_call=None
        )
        report = await service.run("RTX5090")
        self.assertEqual(report.market_refs[PLATFORM_GOOFISH], 10000.0)
        self.assertEqual(report.items[0].price_note, "低于参考价 20%")

    async def test_storage_exception_is_silent(self) -> None:
        item = make_item("g5", "RTX5090 显卡", 8000.0)
        providers = {PLATFORM_GOOFISH: FakeProvider({"RTX5090": [item]})}
        storage = FakeStorage(error=RuntimeError("db down"))
        service = PurchaseDecisionService(
            providers=providers, storage=storage, llm_call=None
        )
        report = await service.run("RTX5090")
        self.assertIsNone(report.market_refs[PLATFORM_GOOFISH])
        self.assertIsNone(report.items[0].price_note)


# ── ⑤ risk_tags / 评分 ───────────────────────────────────────────────────────

class RiskTagsTest(unittest.TestCase):
    def test_goofish_base_and_title_words(self) -> None:
        item = make_item(title="RTX5090 显卡 故障 仅自提")
        tags = risk_tags_for(item)
        self.assertEqual(tags[0], "二手/无发票风险")
        self.assertIn("故障", tags)
        self.assertIn("仅自提", tags)

    def test_taobao_official_shop(self) -> None:
        item = make_item(
            platform=PLATFORM_TAOBAO,
            raw={"shopName": "NVIDIA官方旗舰店", "salesText": "月销100+"},
        )
        self.assertEqual(risk_tags_for(item), ["品牌/官方店铺"])

    def test_taobao_c_shop_and_title_words(self) -> None:
        item = make_item(
            title="RTX5090 工包 拆机",
            platform=PLATFORM_TAOBAO,
            raw={"shopName": "小王数码店"},
        )
        tags = risk_tags_for(item)
        self.assertEqual(tags[0], "淘宝C店/注意验货与评价")
        self.assertIn("工包", tags)
        self.assertIn("拆机", tags)

    def test_score_heuristic_ema_and_risks(self) -> None:
        intent = PurchaseIntent(raw_query="q", keyword="q", attributes={})
        cheap = make_item(title="RTX5090 显卡", price=8000.0)
        self.assertEqual(score_heuristic(cheap, ema=10000.0, intent=intent), 80.0)
        pricey = make_item(title="RTX5090 显卡", price=13000.0)
        self.assertEqual(score_heuristic(pricey, ema=10000.0, intent=intent), 40.0)
        risky = make_item(title="RTX5090 坏 故障 拆修 不退不换", price=8000.0)
        self.assertEqual(
            score_heuristic(risky, ema=10000.0, intent=intent), 80.0 - 24.0
        )

    def test_score_official_bonus_and_new_condition(self) -> None:
        official = make_item(
            title="RTX5090 全新",
            price=10000.0,
            platform=PLATFORM_TAOBAO,
            raw={"shopName": "品牌旗舰店"},
        )
        intent = PurchaseIntent(
            raw_query="q", keyword="q", attributes={}, condition="全新"
        )
        self.assertEqual(
            score_heuristic(official, ema=None, intent=intent), 60.0 + 6.0 + 8.0
        )


# ── ⑥ dedupe ─────────────────────────────────────────────────────────────────

class DedupeTest(unittest.TestCase):
    def test_exact_and_fuzzy_dedupe(self) -> None:
        a = make_item("1", "RTX5090 显卡 全新未拆封", 100.0)
        dup_exact = make_item("1", "另一个标题", 200.0)  # 同 (platform, item_id)
        dup_fuzzy = make_item("2", "RTX5090 显卡 全新未拆封", 100.0)  # 同标题前20字+价格
        other_price = make_item("3", "RTX5090 显卡 全新未拆封", 101.0)
        other_platform = make_item(
            "1", "RTX5090 显卡 全新未拆封", 100.0, platform=PLATFORM_TAOBAO
        )
        out = dedupe_items([a, dup_exact, dup_fuzzy, other_price, other_platform])
        self.assertEqual([i.item_id for i in out], ["1", "3", "1"])
        self.assertIs(out[0], a)
        self.assertEqual(out[2].platform, PLATFORM_TAOBAO)


# ── rank_items LLM / 回退 ────────────────────────────────────────────────────

class RankItemsTest(unittest.IsolatedAsyncioTestCase):
    def _candidates(self) -> list[DecisionItem]:
        cheap = DecisionItem(
            item=make_item("a", "RTX5090 显卡", 9000.0),
            risk_tags=["二手/无发票风险"],
            price_note="低于参考价 10%",
            score=70.0,
        )
        pricey = DecisionItem(
            item=make_item("b", "RTX5090 显卡 箱说全", 12000.0),
            risk_tags=["二手/无发票风险"],
            price_note=None,
            score=55.0,
        )
        return [cheap, pricey]

    async def test_llm_ranking_applied(self) -> None:
        payload = {
            "summary": "优先箱说全的那张。",
            "top": [
                {"item_id": "b", "score": 92, "reason": "箱说全", "risk": "价高"},
                {"item_id": "a", "score": 80, "reason": "便宜", "risk": ""},
            ],
        }
        ranked, summary, used_llm = await rank_items(
            self._candidates(), requirement="买RTX5090", llm_call=make_llm(payload)
        )
        self.assertTrue(used_llm)
        self.assertEqual([d.item.item_id for d in ranked], ["b", "a"])
        self.assertEqual(ranked[0].score, 92.0)
        self.assertEqual(ranked[0].reason, "箱说全")
        self.assertEqual(summary, "优先箱说全的那张。")

    async def test_llm_garbage_falls_back_to_score_order(self) -> None:
        ranked, summary, used_llm = await rank_items(
            self._candidates(), requirement="买RTX5090", llm_call=garbage_llm
        )
        self.assertFalse(used_llm)
        self.assertEqual([d.item.item_id for d in ranked], ["a", "b"])  # score 降序
        self.assertIn("启发式", summary)

    async def test_empty_candidates(self) -> None:
        ranked, summary, used_llm = await rank_items([], requirement="x")
        self.assertEqual(ranked, [])
        self.assertFalse(used_llm)


# ── ⑦ render_decision_card ───────────────────────────────────────────────────

class RenderCardTest(unittest.IsolatedAsyncioTestCase):
    async def test_card_with_degradation_and_error_section(self) -> None:
        l1_item = make_item("g9", "RTX5090 显卡 全新", 12999.0)
        providers = {
            PLATFORM_GOOFISH: FakeProvider({"红色RTX5090": [], "RTX5090": [l1_item]}),
            PLATFORM_TAOBAO: FakeProvider(error=RuntimeError("AUTH_REQUIRED: 需要登录")),
        }
        service = PurchaseDecisionService(
            providers=providers, llm_call=make_llm(INTENT_LLM_PAYLOAD)
        )
        report = await service.run("想买红色RTX5090，预算1万5")
        card = render_decision_card(report)

        self.assertIn("🛒 采购决策：想买红色RTX5090，预算1万5", card)
        self.assertIn("🔍 关键词：RTX5090", card)
        self.assertIn("颜色=红色", card)
        self.assertIn("预算：≤15000 元", card)
        # 降级提示 + hint
        self.assertIn("⚠️ 精确匹配（L0 红色RTX5090）无结果，已降级到 L1：放宽颜色限制", card)
        # 平台分节与参考价（无 EMA → 本批中位数）
        self.assertIn("【闲鱼】1 条 · 参考价 12999 元（本批中位数）", card)
        self.assertIn("二手/无发票风险", card)
        self.assertIn("https://example.com/item?id=g9", card)
        # 失败平台节
        self.assertIn("⚠️ 失败平台：", card)
        self.assertIn("⚠️ 淘宝：AUTH_REQUIRED: 需要登录", card)

    async def test_card_l1_hint_rendered_when_present(self) -> None:
        payload = json.loads(json.dumps(INTENT_LLM_PAYLOAD))
        payload["degradation"][1]["hint"] = "可考虑黑色+RGB调红"
        item = make_item("g10", "RTX5090 显卡", 11000.0)
        providers = {
            PLATFORM_GOOFISH: FakeProvider({"红色RTX5090": [], "RTX5090": [item]}),
        }
        service = PurchaseDecisionService(
            providers=providers, llm_call=make_llm(payload)
        )
        report = await service.run("想买红色RTX5090")
        self.assertEqual(report.level_hint, "可考虑黑色+RGB调红")
        card = render_decision_card(report)
        self.assertIn("💡 可考虑黑色+RGB调红", card)

    async def test_card_ema_ref_and_empty_result(self) -> None:
        providers = {PLATFORM_GOOFISH: FakeProvider({})}
        storage = FakeStorage({("RTX5090", PLATFORM_GOOFISH): 10000.0})
        service = PurchaseDecisionService(
            providers=providers, storage=storage, llm_call=None
        )
        report = await service.run("RTX5090")
        card = render_decision_card(report)
        self.assertIn("均无符合条件", card)
        self.assertNotIn("失败平台", card)

    async def test_card_shows_platform_with_results_below_top_k(self) -> None:
        # 闲鱼有 3 条结果但评分都没进 top_k=1 时，卡片必须露个面，
        # 不能让用户以为该平台没搜到。
        goofish_items = [
            make_item(f"g{i}", f"RTX5090 显卡 拆修 {i}", 9000.0 + i)
            for i in range(3)
        ]
        taobao_item = make_item(
            "t1", "RTX5090 显卡 全新", 11000.0, platform=PLATFORM_TAOBAO,
            raw={"shopName": "ROG旗舰店"},
        )
        providers = {
            PLATFORM_GOOFISH: FakeProvider({"RTX5090": goofish_items}),
            PLATFORM_TAOBAO: FakeProvider({"RTX5090": [taobao_item]}),
        }
        service = PurchaseDecisionService(
            providers=providers, llm_call=None, top_k=1
        )
        report = await service.run("RTX5090")
        self.assertEqual(report.platform_counts.get(PLATFORM_GOOFISH), 3)
        card = render_decision_card(report)
        self.assertIn("【闲鱼】另有 3 条结果，综合评分未进本次推荐", card)


# ── ⑧ 单平台超时/异常不影响另一平台 ──────────────────────────────────────────

class PlatformIsolationTest(unittest.IsolatedAsyncioTestCase):
    async def test_exception_isolated(self) -> None:
        tb_item = make_item(
            "taobao:1",
            "RTX5090 显卡",
            11999.0,
            platform=PLATFORM_TAOBAO,
            raw={"shopName": "品牌旗舰店", "salesText": "月销50+"},
        )
        providers = {
            PLATFORM_GOOFISH: FakeProvider(error=RuntimeError("CAPTCHA: 滑块")),
            PLATFORM_TAOBAO: FakeProvider({"RTX5090": [tb_item]}),
        }
        service = PurchaseDecisionService(providers=providers, llm_call=None)
        report = await service.run("RTX5090")
        self.assertEqual(len(report.items), 1)
        self.assertEqual(report.items[0].item.platform, PLATFORM_TAOBAO)
        self.assertIn(PLATFORM_GOOFISH, report.errors)
        self.assertIn("CAPTCHA", report.errors[PLATFORM_GOOFISH])
        self.assertNotIn(PLATFORM_TAOBAO, report.errors)

    async def test_timeout_isolated(self) -> None:
        tb_item = make_item("taobao:2", "RTX5090 显卡", 11999.0, platform=PLATFORM_TAOBAO)
        providers = {
            PLATFORM_GOOFISH: FakeProvider(delay_sec=5.0),  # 卡死
            PLATFORM_TAOBAO: FakeProvider({"RTX5090": [tb_item]}),
        }
        service = PurchaseDecisionService(
            providers=providers, llm_call=None, per_platform_timeout_sec=1
        )
        report = await service.run("RTX5090")
        self.assertEqual(len(report.items), 1)
        self.assertIn("超时", report.errors[PLATFORM_GOOFISH])
        self.assertNotIn(PLATFORM_TAOBAO, report.errors)


if __name__ == "__main__":
    unittest.main()
