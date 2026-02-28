from __future__ import annotations

import asyncio
import re
import time
from datetime import datetime

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

from .app.config import load_plugin_settings
from .app.notifier import Notifier
from .app.provider import ProviderDependencyError, SearchProvider, build_provider
from .app.recommender import GoofishRecommender
from .app.scheduler import MonitoringScheduler
from .app.storage import SubscriptionStorage
from .app.types import (
    NormalizedItem,
    ProviderError,
    ProviderErrorCode,
    RecommendationCandidate,
    RecommendationResult,
)

PLUGIN_NAME = "astrbot_plugin_goofish_catcher"


class GoofishCatcherPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig | dict | None = None):
        super().__init__(context)
        self.context = context
        self.config = dict(config or {})
        self.settings = load_plugin_settings(self.config, PLUGIN_NAME)

        self.storage: SubscriptionStorage | None = None
        self.provider: SearchProvider | None = None
        self.notifier: Notifier | None = None
        self.recommender: GoofishRecommender | None = None
        self.scheduler: MonitoringScheduler | None = None
        self._provider_error: str | None = None
        self._ready = False
        self._start_lock = asyncio.Lock()

    async def initialize(self) -> None:
        self.storage = SubscriptionStorage(self.settings.db_path)
        await self.storage.initialize()

        self.notifier = Notifier(
            context=self.context,
            webhook_url=self.settings.webhook_url,
            timeout_sec=self.settings.fetch_timeout_sec,
        )
        self.recommender = GoofishRecommender(
            context=self.context,
            settings=self.settings,
        )
        try:
            self.provider = build_provider(self.settings)
        except ProviderDependencyError as exc:
            self._provider_error = str(exc)
            self._ready = True
            logger.error(
                "[goofish_catcher] provider initialization failed: %s",
                self._provider_error,
            )
            return

        self.scheduler = MonitoringScheduler(
            context=self.context,
            settings=self.settings,
            storage=self.storage,
            provider=self.provider,
            notifier=self.notifier,
            recommender=self.recommender,
        )
        self._ready = True
        logger.info(
            "[goofish_catcher] initialized, provider=%s, db=%s",
            self.settings.provider_mode,
            self.settings.db_path,
        )

    @filter.on_astrbot_loaded()
    async def on_astrbot_loaded(self) -> None:
        async with self._start_lock:
            if not self._ready:
                logger.warning("[goofish_catcher] skip start, plugin not ready")
                return
            if self._provider_error:
                logger.warning(
                    "[goofish_catcher] skip scheduler start, provider unavailable: %s",
                    self._provider_error,
                )
                return
            if self.scheduler is None:
                logger.warning("[goofish_catcher] skip start, scheduler is missing")
                return
            await self.scheduler.start()

    async def terminate(self) -> None:
        if self.scheduler is not None:
            await self.scheduler.stop()
        if self.notifier is not None:
            await self.notifier.close()
        if self.provider is not None:
            await self.provider.close()
        if self.storage is not None:
            await self.storage.close()
        self._ready = False

    @filter.command_group("闲鱼", alias={"goofish"})
    async def goofish(self, event: AstrMessageEvent):
        """闲鱼监控指令入口，查看命令总览。"""
        yield event.plain_result(
            "用法：\n"
            "/闲鱼 订阅 <关键词> [interval_sec] [pages]\n"
            "/闲鱼 退订 <关键词>\n"
            "/闲鱼 列表\n"
            "/闲鱼 暂停 <关键词>\n"
            "/闲鱼 恢复 <关键词>\n"
            "/闲鱼 立即检查 [关键词]\n"
            "/闲鱼 查询 <关键词...> [--pages N]\n"
            "/闲鱼 明细 <关键词> [limit]\n"
            "/闲鱼 状态"
        )

    @goofish.command("订阅", alias={"subscribe", "watch"})
    async def subscribe(
        self,
        event: AstrMessageEvent,
        keyword: str,
        interval_sec: int = 0,
        pages: int = 0,
    ):
        """创建或更新关键词订阅，并立即触发一次检查。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        assert self.storage is not None

        interval = (
            interval_sec if interval_sec > 0 else self.settings.default_interval_sec
        )
        page_count = pages if pages > 0 else self.settings.default_pages
        page_count = max(1, min(page_count, self.settings.max_pages))
        interval = max(30, interval)
        umo = event.unified_msg_origin

        subscription, created = await self.storage.upsert_subscription(
            umo=umo,
            keyword=keyword,
            interval_sec=interval,
            pages=page_count,
            drop_abs=self.settings.default_drop_abs,
            drop_pct=self.settings.default_drop_pct,
            new_window_sec=self.settings.default_new_window_sec,
            cooldown_sec=self.settings.default_cooldown_sec,
        )
        await self._ensure_scheduler_started()
        if self.scheduler is not None:
            await self.scheduler.enqueue_manual_check(subscription.id)

        action = "已创建" if created else "已更新"
        message = (
            f"{action}订阅：{keyword}\n"
            f"间隔：{interval}s，页数：{page_count}\n"
            f"降价阈值：￥{subscription.drop_abs:.2f} 或 {subscription.drop_pct:.1%}"
        )
        if self._provider_error:
            message += (
                "\n⚠️ 当前 Provider 不可用，任务不会执行。"
                f"\n原因：{self._provider_error}"
            )
        yield event.plain_result(message)

    @goofish.command("退订", alias={"unsubscribe", "unwatch"})
    async def unsubscribe(self, event: AstrMessageEvent, keyword: str):
        """删除当前会话下指定关键词的订阅。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        assert self.storage is not None

        deleted = await self.storage.delete_subscription(
            event.unified_msg_origin, keyword
        )
        if not deleted:
            yield event.plain_result(f"未找到订阅：{keyword}")
            return
        yield event.plain_result(f"已退订：{keyword}")

    @goofish.command("列表", alias={"list"})
    async def list_subscriptions(self, event: AstrMessageEvent):
        """查看当前会话的订阅列表与运行状态。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        assert self.storage is not None

        subscriptions = await self.storage.list_subscriptions_by_umo(
            event.unified_msg_origin
        )
        if not subscriptions:
            yield event.plain_result("当前会话暂无订阅。")
            return

        lines = ["当前订阅："]
        for sub in subscriptions:
            status = "启用" if sub.enabled else f"暂停({sub.paused_reason or 'manual'})"
            next_run = _format_ts(sub.next_run_at)
            lines.append(
                f"- {sub.keyword} | {status} | 每{sub.interval_sec}s | pages={sub.pages} | 下次={next_run}"
            )
        yield event.plain_result("\n".join(lines))

    @goofish.command("暂停", alias={"pause"})
    async def pause(self, event: AstrMessageEvent, keyword: str):
        """暂停指定关键词订阅，不再参与自动轮询。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        assert self.storage is not None

        sub = await self.storage.get_subscription(event.unified_msg_origin, keyword)
        if sub is None:
            yield event.plain_result(f"未找到订阅：{keyword}")
            return
        await self.storage.pause_subscription(sub.id, "MANUAL_PAUSE")
        yield event.plain_result(f"已暂停订阅：{keyword}")

    @goofish.command("恢复", alias={"resume"})
    async def resume(self, event: AstrMessageEvent, keyword: str):
        """恢复已暂停订阅，并立即入队一次检查。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        assert self.storage is not None

        sub = await self.storage.get_subscription(event.unified_msg_origin, keyword)
        if sub is None:
            yield event.plain_result(f"未找到订阅：{keyword}")
            return
        now_ts = int(time.time())
        await self.storage.resume_subscription(sub.id, now_ts)
        await self._ensure_scheduler_started()
        if self.scheduler is not None:
            await self.scheduler.enqueue_manual_check(sub.id)
        yield event.plain_result(f"已恢复订阅：{keyword}")

    @goofish.command("立即检查", alias={"checknow", "run"})
    async def check_now(self, event: AstrMessageEvent, keyword: str = ""):
        """对订阅执行立即检查并返回推荐；不填关键词则批量入队当前会话全部订阅。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self._provider_error:
            yield event.plain_result(
                f"Provider 当前不可用，无法执行立即检查。\n原因：{self._provider_error}"
            )
            return
        assert self.storage is not None
        assert self.provider is not None
        assert self.recommender is not None
        await self._ensure_scheduler_started()
        if self.scheduler is None:
            yield event.plain_result("调度器未启动。")
            return

        if keyword:
            sub = await self.storage.get_subscription(event.unified_msg_origin, keyword)
            if sub is None:
                yield event.plain_result(f"未找到订阅：{keyword}")
                return
            if not sub.enabled:
                yield event.plain_result(
                    f"订阅 {keyword} 当前处于暂停状态（{sub.paused_reason or 'manual'}），请先执行 /闲鱼 恢复 {keyword}"
                )
                return
            try:
                items = await asyncio.wait_for(
                    self.provider.search(
                        keyword=sub.keyword,
                        pages=max(1, min(sub.pages, self.settings.max_pages)),
                        timeout_sec=self.settings.fetch_timeout_sec,
                    ),
                    timeout=max(self.settings.fetch_timeout_sec + 30, 45),
                )
                now_ts = int(time.time())
                candidates = await self.scheduler.process_manual_fetch(
                    sub=sub,
                    items=items,
                    now_ts=now_ts,
                )
                recommendation = await self.recommender.analyze(
                    umo=event.unified_msg_origin,
                    keyword=sub.keyword,
                    candidates=candidates,
                    top_k=self.settings.llm_top_k,
                )
                yield event.plain_result(_render_recommendation_preview(recommendation))
                return
            except asyncio.TimeoutError:
                yield event.plain_result(
                    f"立即检查超时（>{max(self.settings.fetch_timeout_sec + 30, 45)}s），请稍后重试。"
                )
                return
            except ProviderError as exc:
                if exc.code in {
                    ProviderErrorCode.DEPENDENCY_MISSING,
                    ProviderErrorCode.AUTH_REQUIRED,
                    ProviderErrorCode.CAPTCHA,
                }:
                    await self.storage.pause_subscription(sub.id, exc.code.value)
                yield event.plain_result(
                    f"立即检查失败：{exc.code.value}\n{exc.message}"
                )
                return
            except Exception as exc:
                yield event.plain_result(f"立即检查失败：{exc}")
                return

        enqueued = 0
        subscriptions = await self.storage.list_subscriptions_by_umo(
            event.unified_msg_origin
        )
        for sub in subscriptions:
            if not sub.enabled:
                continue
            if await self.scheduler.enqueue_manual_check(sub.id):
                enqueued += 1

        if enqueued == 0:
            yield event.plain_result("没有任务被加入队列（可能已在执行或队列已满）。")
            return
        yield event.plain_result(f"已提交 {enqueued} 个任务到检查队列。")

    @goofish.command("查询", alias={"query", "search", "inspect"})
    async def query_once(
        self,
        event: AstrMessageEvent,
        keyword: str = "",
    ):
        """免订阅查询：整段关键词可包含空格，可选 --pages/-p 指定页数。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        if self._provider_error:
            yield event.plain_result(
                f"Provider 当前不可用，无法执行查询。\n原因：{self._provider_error}"
            )
            return
        assert self.provider is not None
        assert self.recommender is not None

        raw_query_args = (
            _extract_subcommand_args(event.get_message_str()) or str(keyword).strip()
        )
        keyword_text, page_count = _parse_query_input(
            raw_keyword=raw_query_args,
            default_pages=self.settings.default_pages,
            max_pages=self.settings.max_pages,
        )
        if not keyword_text:
            yield event.plain_result(
                "关键词不能为空。示例：/闲鱼 查询 适马 60-600 --pages 2"
            )
            return
        timeout_sec = max(self.settings.fetch_timeout_sec + 30, 45)
        try:
            raw_items = await asyncio.wait_for(
                self.provider.search(
                    keyword=keyword_text,
                    pages=page_count,
                    timeout_sec=self.settings.fetch_timeout_sec,
                ),
                timeout=timeout_sec,
            )
            filtered_items, filter_mode = await self.recommender.prefilter_items(
                umo=event.unified_msg_origin,
                keyword=keyword_text,
                items=raw_items,
            )
            candidates = _build_query_candidates(
                keyword=keyword_text,
                items=filtered_items,
                observed_at=int(time.time()),
            )
            recommendation = await self.recommender.analyze(
                umo=event.unified_msg_origin,
                keyword=keyword_text,
                candidates=candidates,
                top_k=self.settings.llm_top_k,
            )
            yield event.plain_result(
                _render_query_recommendation_preview(
                    recommendation=recommendation,
                    page_count=page_count,
                    raw_total=len(raw_items),
                    filtered_total=len(filtered_items),
                    filter_mode=filter_mode,
                )
            )
            return
        except asyncio.TimeoutError:
            yield event.plain_result(f"查询超时（>{timeout_sec}s），请稍后重试。")
            return
        except ProviderError as exc:
            yield event.plain_result(f"查询失败：{exc.code.value}\n{exc.message}")
            return
        except Exception as exc:
            yield event.plain_result(f"查询失败：{exc}")
            return

    @goofish.command("明细", alias={"detail", "items"})
    async def detail(
        self,
        event: AstrMessageEvent,
        keyword: str,
        limit: int = 10,
    ):
        """查看订阅最近一次缓存快照，不触发新抓取。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        assert self.storage is not None

        sub = await self.storage.get_subscription(event.unified_msg_origin, keyword)
        if sub is None:
            yield event.plain_result(f"未找到订阅：{keyword}")
            return

        limit = max(1, min(limit, 30))
        if sub.last_run_at is None:
            yield event.plain_result(
                f"订阅 {keyword} 暂无缓存结果。先执行 /闲鱼 立即检查 {keyword}"
            )
            return

        snapshot_ts = int(sub.last_run_at)
        items, total = await self.storage.list_items_by_snapshot(
            sub_id=sub.id,
            snapshot_ts=snapshot_ts,
            limit=limit,
        )
        yield event.plain_result(
            _render_items_detail(
                sub.keyword,
                items,
                limit=limit,
                total=total,
                snapshot_ts=snapshot_ts,
            )
        )

    @goofish.command("状态", alias={"status"})
    async def status(self, event: AstrMessageEvent):
        """查看调度器、Provider 与当前会话订阅的运行状态。"""
        if not await self._check_ready(event):
            yield event.plain_result("插件尚未完成初始化，请稍后再试。")
            return
        assert self.storage is not None

        await self._ensure_scheduler_started()
        scheduler_status = (
            await self.scheduler.get_status() if self.scheduler is not None else {}
        )
        umo_subscriptions = await self.storage.list_subscriptions_by_umo(
            event.unified_msg_origin
        )
        enabled_local = sum(1 for sub in umo_subscriptions if sub.enabled)
        paused_local = len(umo_subscriptions) - enabled_local

        yield event.plain_result(
            "闲鱼监控状态：\n"
            f"- 运行中：{scheduler_status.get('running', False)}\n"
            f"- 队列长度：{scheduler_status.get('queue_size', 0)}\n"
            f"- 执行中：{scheduler_status.get('inflight', 0)}\n"
            f"- Worker 数：{scheduler_status.get('workers', 0)}\n"
            f"- 当前会话订阅：{len(umo_subscriptions)}（启用 {enabled_local} / 暂停 {paused_local}）\n"
            f"- 全局启用订阅：{scheduler_status.get('enabled_subscriptions', 0)}\n"
            f"- Provider：{self.settings.provider_mode}\n"
            f"- Provider 可用：{self._provider_error is None}\n"
            f"- Provider 错误：{self._provider_error or '-'}\n"
            f"- DB：{self.settings.db_path}"
        )

    async def _ensure_scheduler_started(self) -> None:
        if self.scheduler is None:
            return
        if self.scheduler.running:
            return
        async with self._start_lock:
            if not self.scheduler.running:
                await self.scheduler.start()

    async def _check_ready(self, event: AstrMessageEvent) -> bool:
        if self._ready and self.storage is not None:
            return True
        logger.warning("[goofish_catcher] command called before ready")
        return False


def _format_ts(ts: int | None) -> str:
    if ts is None:
        return "-"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def _render_recommendation_preview(recommendation: RecommendationResult) -> str:
    lines = [
        f"【立即检查】关键词：{recommendation.keyword}",
        f"候选数：{recommendation.total_candidates} | 推荐数：{len(recommendation.top)}",
        f"分析方式：{'LLM' if recommendation.used_llm else 'Heuristic'}",
        f"总体建议：{recommendation.summary}",
    ]
    if recommendation.fallback_reason:
        lines.append(f"回退原因：{recommendation.fallback_reason}")

    if not recommendation.top:
        lines.append(f"查看逐条请用 /闲鱼 明细 {recommendation.keyword}")
        return "\n".join(lines)

    for idx, item in enumerate(recommendation.top, start=1):
        lines.append(f"{idx}. [{item.score:.1f}] {item.title}")
        lines.append(f"   价格：￥{item.price:.2f}")
        lines.append(f"   理由：{item.reason}")
        lines.append(f"   风险：{item.risk}")
        lines.append(f"   链接：{item.url}")
    lines.append(f"查看逐条请用 /闲鱼 明细 {recommendation.keyword}")
    return "\n".join(lines)


def _build_query_candidates(
    keyword: str,
    items: list[NormalizedItem],
    observed_at: int,
) -> list[RecommendationCandidate]:
    return [
        RecommendationCandidate(
            event_type="NEW",
            keyword=keyword,
            item_id=item.item_id,
            title=item.title,
            price=item.price,
            url=item.url,
            publish_time=item.publish_time,
            observed_at=observed_at,
        )
        for item in items
    ]


def _extract_subcommand_args(message: str) -> str:
    normalized = re.sub(r"\s+", " ", message.strip())
    if not normalized:
        return ""
    parts = normalized.split(" ", 2)
    if len(parts) < 3:
        return ""
    return parts[2].strip()


def _parse_query_input(
    raw_keyword: str,
    *,
    default_pages: int,
    max_pages: int,
) -> tuple[str, int]:
    text = raw_keyword.strip()
    page_count = max(1, min(default_pages, max_pages))
    if not text:
        return "", page_count

    matched = re.search(r"(?:^|\s)(?:--pages|-p)\s+(\d+)\s*$", text)
    if matched:
        page_count = max(1, min(int(matched.group(1)), max_pages))
        text = text[: matched.start()].strip()
    return text, page_count


def _render_query_recommendation_preview(
    recommendation: RecommendationResult,
    *,
    page_count: int,
    raw_total: int,
    filtered_total: int,
    filter_mode: str,
) -> str:
    lines = [
        f"【查询推荐】关键词：{recommendation.keyword}",
        f"抓取页数：{page_count} | 原始结果：{raw_total} | 初筛后：{filtered_total}",
        f"初筛模式：{filter_mode}",
        f"候选数：{recommendation.total_candidates} | 推荐数：{len(recommendation.top)}",
        f"分析方式：{'LLM' if recommendation.used_llm else 'Heuristic'}",
        f"总体建议：{recommendation.summary}",
    ]
    if recommendation.fallback_reason:
        lines.append(f"回退原因：{recommendation.fallback_reason}")

    if not recommendation.top:
        lines.append("未产出可推荐条目，请尝试更精确的关键词后重试。")
        return "\n".join(lines)

    for idx, item in enumerate(recommendation.top, start=1):
        lines.append(f"{idx}. [{item.score:.1f}] {item.title}")
        lines.append(f"   价格：￥{item.price:.2f}")
        lines.append(f"   理由：{item.reason}")
        lines.append(f"   风险：{item.risk}")
        lines.append(f"   链接：{item.url}")
    lines.append(f"可再次执行 /闲鱼 查询 {recommendation.keyword}")
    return "\n".join(lines)


def _render_items_detail(
    keyword: str,
    items: list[NormalizedItem],
    limit: int = 10,
    total: int | None = None,
    snapshot_ts: int | None = None,
) -> str:
    total_count = total if total is not None else len(items)
    if not items:
        if snapshot_ts is None:
            return f"【明细】关键词：{keyword}\n暂无缓存商品。"
        return (
            f"【明细】关键词：{keyword}\n"
            f"最近一次缓存时间：{_format_ts(snapshot_ts)}\n"
            "该次结果为 0 条商品。"
        )

    top = items[:limit]
    lines = [
        f"【明细】关键词：{keyword}",
        f"最近一次缓存时间：{_format_ts(snapshot_ts) if snapshot_ts else '-'}",
        f"该次缓存共 {total_count} 条，展示前 {len(top)} 条：",
    ]
    for idx, item in enumerate(top, start=1):
        lines.append(f"{idx}. {item.title}")
        lines.append(f"   价格：￥{item.price:.2f}")
        lines.append(f"   链接：{item.url}")
    return "\n".join(lines)
