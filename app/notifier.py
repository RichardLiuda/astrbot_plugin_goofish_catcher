from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from astrbot.api import logger
from astrbot.api.event import MessageChain
from astrbot.api.star import Context

from .detector import EventPayload
from .types import NormalizedItem, RecommendationResult


class Notifier:
    def __init__(
        self,
        *,
        context: Context,
        webhook_url: str | None = None,
        timeout_sec: int = 20,
    ) -> None:
        self.context = context
        self.webhook_url = webhook_url
        self.timeout_sec = timeout_sec
        self._client: httpx.AsyncClient | None = None

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout_sec)
        return self._client

    async def send_new(
        self,
        *,
        umo: str,
        keyword: str,
        item: NormalizedItem,
        observed_at: int,
    ) -> bool:
        publish_time_text = _format_time(item.publish_time or observed_at)
        text = (
            f"🆕【闲鱼上新】关键词：{keyword}\n"
            f"{item.title}\n"
            f"价格：¥{item.price:.2f}\n"
            f"时间：{publish_time_text}\n"
            f"链接：{item.url}"
        )
        sent = await self._send_to_umo(umo, text)
        payload = EventPayload(
            event_type="NEW",
            keyword=keyword,
            item_id=item.item_id,
            title=item.title,
            price=item.price,
            url=item.url,
            publish_time=item.publish_time,
            observed_at=observed_at,
        )
        await self._send_webhook(payload.to_dict())
        return sent

    async def send_price_drop(
        self,
        *,
        umo: str,
        keyword: str,
        item: NormalizedItem,
        last_price: float,
        drop_abs: float,
        drop_pct: float,
        observed_at: int,
    ) -> bool:
        text = (
            f"📉【闲鱼降价】关键词：{keyword}\n"
            f"{item.title}\n"
            f"现价：¥{item.price:.2f}（上次：¥{last_price:.2f}）\n"
            f"降幅：¥{drop_abs:.2f}（{drop_pct:.1%}）\n"
            f"链接：{item.url}"
        )
        sent = await self._send_to_umo(umo, text)
        payload = EventPayload(
            event_type="PRICE_DROP",
            keyword=keyword,
            item_id=item.item_id,
            title=item.title,
            price=item.price,
            url=item.url,
            publish_time=item.publish_time,
            observed_at=observed_at,
            drop_abs=drop_abs,
            drop_pct=drop_pct,
            last_price=last_price,
        )
        await self._send_webhook(payload.to_dict())
        return sent

    async def send_alert(
        self,
        *,
        umo: str,
        keyword: str,
        code: str,
        message: str,
    ) -> bool:
        text = (
            f"⚠️【闲鱼监控告警】关键词：{keyword}\n"
            f"错误码：{code}\n"
            f"说明：{message}\n"
            "已暂停该订阅，请处理后手动恢复。"
        )
        sent = await self._send_to_umo(umo, text)
        await self._send_webhook(
            {
                "event_type": "ALERT",
                "keyword": keyword,
                "error_code": code,
                "message": message,
            }
        )
        return sent

    async def send_recommendation_summary(
        self,
        *,
        umo: str,
        recommendation: RecommendationResult,
    ) -> bool:
        lines = [
            f"【闲鱼建议】关键词：{recommendation.keyword}",
            f"候选数：{recommendation.total_candidates} | 推荐数：{len(recommendation.top)}",
            f"分析方式：{'LLM' if recommendation.used_llm else 'Heuristic'}",
            f"总体建议：{recommendation.summary}",
        ]
        if recommendation.fallback_reason:
            lines.append(
                f"回退原因：{_readable_fallback_reason(recommendation.fallback_reason)}"
            )

        for idx, item in enumerate(recommendation.top, start=1):
            lines.append(f"{idx}. [{item.score:.1f}] {item.title}")
            lines.append(f"   价格：￥{item.price:.2f}")
            lines.append(f"   理由：{item.reason}")
            lines.append(f"   风险：{item.risk}")
            lines.append(f"   链接：{item.url}")

        lines.append(f"查看逐条请用 /闲鱼 明细 {recommendation.keyword}")
        text = "\n".join(lines)
        sent = await self._send_to_umo(umo, text)
        await self._send_webhook(
            {
                "event_type": "RECOMMENDATION_SUMMARY",
                "keyword": recommendation.keyword,
                "summary": recommendation.summary,
                "total_candidates": recommendation.total_candidates,
                "used_llm": recommendation.used_llm,
                "fallback_reason": recommendation.fallback_reason,
                "top": [
                    {
                        "item_id": item.item_id,
                        "score": item.score,
                        "reason": item.reason,
                        "risk": item.risk,
                        "title": item.title,
                        "price": item.price,
                        "url": item.url,
                    }
                    for item in recommendation.top
                ],
            }
        )
        return sent

    async def _send_to_umo(self, umo: str, text: str) -> bool:
        try:
            await self.context.send_message(umo, MessageChain().message(text))
            return True
        except Exception as exc:
            logger.error(
                "[goofish_catcher] send_message failed: %s", exc, exc_info=True
            )
            return False

    async def _send_webhook(self, payload: dict[str, Any]) -> None:
        if not self.webhook_url:
            return
        client = await self._ensure_client()
        try:
            response = await client.post(self.webhook_url, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "[goofish_catcher] webhook post failed: status=%s body=%s",
                exc.response.status_code,
                exc.response.text[:200],
            )
        except Exception as exc:
            logger.warning("[goofish_catcher] webhook post failed: %s", exc)


def _format_time(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _readable_fallback_reason(reason: str) -> str:
    mapping = {
        "LLM_TIMEOUT": "AI 分析超时，已使用本地规则回退",
        "NO_PROVIDER": "未找到可用的 AI 模型，已使用本地规则回退",
        "LLM_DISABLED": "AI 分析已关闭，已使用本地规则回退",
        "LLM_EXCEPTION": "AI 服务异常，已使用本地规则回退",
        "LLM_EMPTY": "AI 返回为空，已使用本地规则回退",
        "LLM_JSON_INVALID": "AI 输出格式异常，已使用本地规则回退",
        "LLM_JSON_UNUSABLE": "AI 输出不可用，已使用本地规则回退",
        "NO_CANDIDATE": "本轮没有可分析的候选商品",
    }
    return mapping.get(reason, f"已触发回退策略（{reason}）")
