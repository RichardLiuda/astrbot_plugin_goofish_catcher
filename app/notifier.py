from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from astrbot.api import logger
from astrbot.api.event import MessageChain
from astrbot.api.message_components import Image, Plain
from astrbot.api.star import Context

from .detector import EventPayload
from .platforms import platform_display_name, split_item_id
from .reply_favorite import recommendation_reply_hint
from .types import DEFAULT_PLATFORM, NormalizedItem, RecommendationResult


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
            f"🆕【{_platform_display_from_item_id(item.item_id)}上新】关键词：{keyword}\n"
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
            f"📉【{_platform_display_from_item_id(item.item_id)}降价】关键词：{keyword}\n"
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
        action_hint: str | None = None,
    ) -> bool:
        text = (
            f"⚠️【闲鱼监控告警】关键词：{keyword}\n"
            f"错误码：{code}\n"
            f"说明：{message}\n"
            f"{action_hint or '已暂停该订阅，请处理后手动恢复。'}"
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
        # RecommendationResult 不携带平台字段，从首个推荐项的 item_id 推断；top 为空默认闲鱼
        top_item_id = recommendation.top[0].item_id if recommendation.top else ""
        lines = [
            f"【{_platform_display_from_item_id(top_item_id)}建议】关键词：{recommendation.keyword}",
            f"候选数：{recommendation.total_candidates} | 推荐数：{len(recommendation.top)}",
            f"分析方式：{'LLM' if recommendation.used_llm else 'Heuristic'}",
            f"总体建议：{recommendation.summary}",
        ]
        if recommendation.fallback_reason:
            lines.append(
                f"回退原因：{_readable_fallback_reason(recommendation.fallback_reason)}"
            )

        for idx, item in enumerate(recommendation.top, start=1):
            lines.extend(_render_recommendation_item_lines(idx, item))

        lines.append(recommendation_reply_hint())
        # /闲鱼 明细 只查 goofish 订阅，对其他平台是死胡同，不输出该提示
        if split_item_id(top_item_id)[0] == DEFAULT_PLATFORM:
            lines.append(f"查看逐条请用 /闲鱼 明细 {recommendation.keyword}")
        text = "\n".join(lines)
        sent = await self._send_chain_to_umo(
            umo,
            _build_recommendation_chain(lines, recommendation),
            fallback_text=text,
        )
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
                        "deep_analysis": (
                            item.deep_analysis.to_dict()
                            if item.deep_analysis is not None
                            else None
                        ),
                    }
                    for item in recommendation.top
                ],
            }
        )
        return sent

    async def broadcast_alert(
        self,
        *,
        code: str,
        message: str,
        umos: list[str] | None = None,
    ) -> None:
        """Send an alert to a list of umos (or no-op when umos is empty).

        Callers should resolve the umo list from storage.get_all_subscriber_umos()
        before calling this method.
        """
        if not umos:
            return
        text = (
            f"⚠️【闲鱼监控告警】\n"
            f"错误码：{code}\n"
            f"说明：{message}"
        )
        for umo in umos:
            try:
                await self._send_to_umo(umo, text)
            except Exception as exc:
                logger.warning(
                    "[goofish_catcher] broadcast_alert to umo=%s failed: %s",
                    umo,
                    exc,
                )
        await self._send_webhook(
            {"event_type": "ALERT", "error_code": code, "message": message}
        )

    async def _send_to_umo(self, umo: str, text: str) -> bool:
        return await self._send_chain_to_umo(
            umo,
            MessageChain().message(text),
            fallback_text=text,
        )

    async def _send_chain_to_umo(
        self,
        umo: str,
        chain: MessageChain,
        *,
        fallback_text: str,
    ) -> bool:
        if not _is_valid_unified_msg_origin(umo):
            logger.error(
                "[goofish_catcher] invalid umo=%r, cannot send message. "
                "Expected AstrBot unified_msg_origin format like "
                "'platform:MessageType:session_id'.",
                umo,
            )
            return False
        try:
            await self.context.send_message(umo, chain)
            return True
        except Exception as exc:
            logger.warning(
                "[goofish_catcher] send rich message failed, retrying text-only: %s",
                exc,
                exc_info=True,
            )
            try:
                await self.context.send_message(umo, MessageChain().message(fallback_text))
                return True
            except Exception as text_exc:
                logger.error(
                    "[goofish_catcher] send_message failed: %s", text_exc, exc_info=True
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


def _platform_display_from_item_id(item_id: str | None) -> str:
    """从 item_id 推断平台中文显示名；空或未知一律按闲鱼处理。"""
    platform, _ = split_item_id(item_id or "")
    return platform_display_name(platform)


def _is_valid_unified_msg_origin(umo: str) -> bool:
    if not isinstance(umo, str):
        return False
    parts = umo.split(":", 2)
    return len(parts) == 3 and all(part.strip() for part in parts)


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


def _build_recommendation_chain(
    header_lines: list[str],
    recommendation: RecommendationResult,
) -> MessageChain:
    if not recommendation.top:
        return MessageChain([Plain("\n".join(header_lines))])

    chain_parts: list[object] = []
    preface_count = 4 + (1 if recommendation.fallback_reason else 0)
    chain_parts.append(Plain("\n".join(header_lines[:preface_count]) + "\n"))
    for idx, item in enumerate(recommendation.top, start=1):
        analysis = item.deep_analysis
        image_url = analysis.image_urls[0] if analysis and analysis.image_urls else None
        text_lines = [
            f"\n{idx}. [{item.score:.1f}] {item.title}",
            f"价格：￥{item.price:.2f}",
            f"理由：{item.reason}",
            f"风险：{item.risk}",
        ]
        if analysis is not None:
            text_lines.extend(
                [
                    f"信用：{analysis.credit_status}（{analysis.credit_reason}）",
                    f"深度分析：{analysis.summary}",
                ]
            )
        if image_url:
            text_lines.append("主图：")
            chain_parts.append(Plain("\n".join(text_lines) + "\n"))
            try:
                chain_parts.append(Image.fromURL(image_url))
            except Exception:
                chain_parts.append(Plain(f"{image_url}\n"))
            chain_parts.append(Plain(f"\n链接：{item.url}\n"))
        else:
            text_lines.append(f"链接：{item.url}")
            chain_parts.append(Plain("\n".join(text_lines) + "\n"))
    tail = "\n" + recommendation_reply_hint()
    # /闲鱼 明细 只查 goofish 订阅，对其他平台是死胡同，不输出该提示
    if split_item_id(recommendation.top[0].item_id)[0] == DEFAULT_PLATFORM:
        tail += f"\n查看逐条请用 /闲鱼 明细 {recommendation.keyword}"
    chain_parts.append(Plain(tail))
    return MessageChain(chain_parts)


def _render_recommendation_item_lines(idx: int, item) -> list[str]:
    lines = [
        f"{idx}. [{item.score:.1f}] {item.title}",
        f"   价格：￥{item.price:.2f}",
        f"   理由：{item.reason}",
        f"   风险：{item.risk}",
    ]
    analysis = item.deep_analysis
    if analysis is not None:
        lines.append(
            f"   信用：{analysis.credit_status}（{analysis.credit_reason or '暂无说明'}）"
        )
        if analysis.summary:
            lines.append(f"   深度分析：{analysis.summary}")
        if analysis.risk:
            lines.append(f"   详情风险：{analysis.risk}")
        heat = []
        if analysis.want_count is not None:
            heat.append(f"想要 {analysis.want_count}")
        if analysis.browse_count is not None:
            heat.append(f"浏览 {analysis.browse_count}")
        if heat:
            lines.append(f"   热度：{' / '.join(heat)}")
        if analysis.image_urls:
            lines.append(f"   主图：{analysis.image_urls[0]}")
    else:
        lines.append("   深度分析：未获取到详情，按保守规则不过滤")
    lines.append(f"   链接：{item.url}")
    return lines
