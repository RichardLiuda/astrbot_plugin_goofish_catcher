from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import aiosqlite

from .admin_types import (
    AdminOverview,
    EditablePluginConfig,
    ItemDetail,
    ProviderHealthSnapshot,
    QueryPreview,
    QueryPreviewItem,
    SubscriptionSummary,
)
from .config import (
    DEFAULT_ADMIN_WEBUI_HOST,
    DEFAULT_ADMIN_WEBUI_PORT,
    PROVIDER_MODE_PLAYWRIGHT_LOCAL,
    PROVIDER_MODE_REMOTE_REST,
    get_runtime_override_path,
    load_plugin_settings,
    save_runtime_overrides,
)
from .types import (
    ProviderError,
    RecommendationCandidate,
    RecommendationResult,
    Subscription,
)


class AdminService:
    def __init__(self, plugin: Any) -> None:
        self.plugin = plugin
        self._config_schema_cache: dict[str, Any] | None = None

    @property
    def settings(self):
        return self.plugin.settings

    @property
    def storage(self):
        storage = self.plugin.storage
        if storage is None:
            raise RuntimeError("storage is not initialized")
        return storage

    @property
    def provider(self):
        provider = self.plugin.provider
        if provider is None:
            raise RuntimeError(self.plugin._provider_error or "provider is unavailable")
        return provider

    @property
    def recommender(self):
        recommender = self.plugin.recommender
        if recommender is None:
            raise RuntimeError("recommender is not initialized")
        return recommender

    @property
    def activity_monitor(self):
        return self.plugin.activity_monitor

    @property
    def scheduler(self):
        scheduler = self.plugin.scheduler
        if scheduler is None:
            raise RuntimeError("scheduler is not initialized")
        return scheduler

    async def get_overview(self) -> dict[str, Any]:
        health_snapshot = await self._get_provider_health_snapshot(refresh=False)
        scheduler_status = {}
        if self.plugin.scheduler is not None:
            scheduler_status = await self.plugin.scheduler.get_status()

        enabled = await self.storage.count_enabled_subscriptions()
        total = await self.storage.count_subscriptions()
        paused = await self.storage.count_paused_subscriptions()
        success_count, failed_count = await self.storage.get_recent_run_stats(
            since_ts=int(time.time()) - 86400
        )
        total_runs = success_count + failed_count
        success_rate = (success_count / total_runs * 100.0) if total_runs else 0.0
        overview = AdminOverview(
            provider_mode=self.settings.provider_mode,
            provider_available=self.plugin._provider_error is None,
            provider_error=self.plugin._provider_error,
            scheduler_running=bool(scheduler_status.get("running", False)),
            queue_size=int(scheduler_status.get("queue_size", 0)),
            inflight=int(scheduler_status.get("inflight", 0)),
            workers=int(scheduler_status.get("workers", 0)),
            enabled_subscriptions=enabled,
            paused_subscriptions=paused,
            total_subscriptions=total,
            success_runs_24h=success_count,
            failed_runs_24h=failed_count,
            success_rate_24h=round(success_rate, 1),
            recent_alerts=await self.storage.list_recent_alerts(limit=8),
            trends=await self.storage.list_notification_trends(
                since_ts=int(time.time()) - 7 * 86400,
                limit_days=7,
            ),
            provider_health=health_snapshot["details"],
            provider_health_checked_at=health_snapshot["checked_at"],
        )
        return asdict(overview)

    async def list_subscriptions(
        self,
        *,
        keyword: str = "",
        umo: str = "",
        status: str = "all",
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        enabled: bool | None = None
        if status == "enabled":
            enabled = True
        elif status == "paused":
            enabled = False
        rows, total = await self.storage.list_subscriptions_paginated(
            keyword=keyword,
            umo=umo,
            enabled=enabled,
            limit=limit,
            offset=offset,
        )
        return {
            "items": [asdict(self._to_subscription_summary(row)) for row in rows],
            "total": total,
        }

    async def create_subscription(self, payload: dict[str, Any]) -> dict[str, Any]:
        values = self._normalize_subscription_payload(payload)
        subscription, created = await self.storage.upsert_subscription(**values)
        await self.plugin._ensure_scheduler_started()
        if self.plugin.scheduler is not None:
            await self.plugin.scheduler.enqueue_manual_check(subscription.id)
        return {
            "created": created,
            "subscription": asdict(self._to_subscription_summary(subscription)),
        }

    async def update_subscription(self, sub_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        current = await self.storage.get_subscription_by_id(sub_id)
        if current is None:
            raise KeyError("subscription not found")
        values = self._normalize_subscription_payload(payload, current=current)
        try:
            updated = await self.storage.update_subscription(
                sub_id=sub_id,
                **values,
            )
        except aiosqlite.IntegrityError as exc:
            raise ValueError("subscription keyword already exists for this UMO") from exc
        if updated is None:
            raise KeyError("subscription not found")
        return {"subscription": asdict(self._to_subscription_summary(updated))}

    async def delete_subscription(self, sub_id: int) -> dict[str, Any]:
        deleted = await self.storage.delete_subscription_by_id(sub_id)
        if not deleted:
            raise KeyError("subscription not found")
        return {"deleted": True}

    async def pause_subscription(self, sub_id: int) -> dict[str, Any]:
        sub = await self.storage.get_subscription_by_id(sub_id)
        if sub is None:
            raise KeyError("subscription not found")
        await self.storage.pause_subscription(sub.id, "ADMIN_PAUSE")
        updated = await self.storage.get_subscription_by_id(sub_id)
        return {"subscription": asdict(self._to_subscription_summary(updated or sub))}

    async def resume_subscription(self, sub_id: int) -> dict[str, Any]:
        sub = await self.storage.get_subscription_by_id(sub_id)
        if sub is None:
            raise KeyError("subscription not found")
        now_ts = int(time.time())
        await self.storage.resume_subscription(sub.id, now_ts)
        await self.plugin._ensure_scheduler_started()
        if self.plugin.scheduler is not None:
            await self.plugin.scheduler.enqueue_manual_check(sub.id)
        updated = await self.storage.get_subscription_by_id(sub_id)
        return {"subscription": asdict(self._to_subscription_summary(updated or sub))}

    async def check_subscription(self, sub_id: int) -> dict[str, Any]:
        sub = await self.storage.get_subscription_by_id(sub_id)
        if sub is None:
            raise KeyError("subscription not found")
        preview = await self._run_manual_subscription_check(sub)
        return {"recommendation": preview}

    async def query(self, payload: dict[str, Any]) -> dict[str, Any]:
        keyword = str(payload.get("keyword", "")).strip()
        if not keyword:
            raise ValueError("keyword is required")
        page_count = int(payload.get("pages", self.settings.default_pages) or self.settings.default_pages)
        page_count = max(1, min(page_count, self.settings.max_pages))
        preview = await self._run_query(keyword=keyword, page_count=page_count)
        return {"preview": preview}

    async def list_subscription_options(self) -> dict[str, Any]:
        options = await self.storage.list_subscription_options()
        return {
            "items": [asdict(option) for option in options],
            "total": len(options),
        }

    async def list_items(
        self,
        *,
        search: str = "",
        sub_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort_by: str = "last_seen_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        items, total = await self.storage.list_item_summaries(
            search=search,
            sub_id=sub_id,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )
        return {
            "items": [asdict(item) for item in items],
            "total": total,
        }

    async def list_items_by_subscription(
        self,
        *,
        search: str = "",
        sub_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        sort_by: str = "last_seen_at",
        sort_order: str = "desc",
        limit: int = 120,
        offset: int = 0,
    ) -> dict[str, Any]:
        items, total = await self.storage.list_items_by_subscription(
            search=search,
            sub_id=sub_id,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )
        return {
            "items": [asdict(item) for item in items],
            "total": total,
        }

    async def delete_items(self, item_ids: list[str], sub_id: int = 0) -> dict[str, Any]:
        deleted = await self.storage.delete_items_bulk(sub_id, item_ids)
        return {"deleted": deleted}

    async def get_item_detail(self, item_id: str) -> dict[str, Any]:
        summary = await self.storage.get_item_summary(item_id)
        if summary is None:
            raise KeyError("item not found")
        detail = ItemDetail(
            item=summary,
            subscriptions=await self.storage.list_related_subscriptions_for_item(item_id),
            price_history=await self.storage.list_price_history_for_item(item_id, limit=120),
            notifications=await self.storage.list_notifications_for_item(item_id, limit=50),
            fetch_runs=await self.storage.list_fetch_runs_for_item(item_id, limit=30),
        )
        return asdict(detail)

    async def list_fetch_runs(
        self,
        *,
        status: str = "",
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        runs, total = await self.storage.list_fetch_runs(
            status=status,
            limit=limit,
            offset=offset,
        )
        return {
            "items": [asdict(run) for run in runs],
            "total": total,
        }

    async def get_activity_monitor(self) -> dict[str, Any]:
        scheduler_status = {}
        if self.plugin.scheduler is not None:
            scheduler_status = await self.plugin.scheduler.get_status()
        snapshot = await self.activity_monitor.snapshot()
        snapshot["summary"].update(
            {
                "queue_size": int(scheduler_status.get("queue_size", 0)),
                "inflight": int(scheduler_status.get("inflight", 0)),
                "workers": int(scheduler_status.get("workers", 0)),
                "scheduler_running": bool(scheduler_status.get("running", False)),
            }
        )
        return snapshot

    async def get_provider_health(self, *, refresh: bool = False) -> dict[str, Any]:
        return await self._get_provider_health_snapshot(refresh=refresh)

    async def _get_provider_health_snapshot(self, *, refresh: bool) -> dict[str, Any]:
        await self._sync_provider_health(refresh=refresh)

        ok = self.plugin._provider_error is None
        remote_details = self.plugin._provider_health or {}
        storage_state = self._resolve_storage_state(remote_details)
        payload = ProviderHealthSnapshot(
            ok=ok,
            provider=self.settings.provider_mode,
            auth=self._resolve_auth_status(remote_details, storage_state=storage_state),
            storage_state=storage_state,
            checked_at=self.plugin._provider_health_checked_at,
            details=self._normalize_provider_health_details(
                remote_details,
                auth=self._resolve_auth_status(remote_details, storage_state=storage_state),
                storage_state=storage_state,
            ),
        )
        data = asdict(payload)
        data["provider_error"] = self.plugin._provider_error
        return data

    async def _sync_provider_health(self, *, refresh: bool) -> None:
        checked_at = int(self.plugin._provider_health_checked_at or 0)
        now_ts = int(time.time())
        should_refresh = refresh or checked_at <= 0 or (now_ts - checked_at >= 8)
        if not should_refresh:
            return
        try:
            await self.plugin.refresh_provider_health(force=True)
        except ProviderError:
            # refresh_provider_health already stores latest error snapshot on plugin
            return

    def _resolve_storage_state(self, remote_details: dict[str, Any]) -> bool | None:
        if self.settings.provider_mode == PROVIDER_MODE_REMOTE_REST:
            value = remote_details.get("storage_state")
            return None if value is None else bool(value)
        return bool(
            self.settings.playwright_storage_state_path
            and self.settings.playwright_storage_state_path.exists()
        )

    def _resolve_auth_status(
        self,
        remote_details: dict[str, Any],
        *,
        storage_state: bool | None,
    ) -> str | None:
        if self.settings.provider_mode == PROVIDER_MODE_REMOTE_REST:
            auth = str(remote_details.get("auth") or "").strip()
            if auth:
                return auth
            if storage_state is True:
                return "远端登录态已就绪"
            if storage_state is False:
                return "远端登录态缺失"
            return "-"

        if self.settings.provider_mode == PROVIDER_MODE_PLAYWRIGHT_LOCAL:
            return "本地登录态已就绪" if storage_state else "本地登录态缺失"

        return "-"

    def _normalize_provider_health_details(
        self,
        remote_details: dict[str, Any],
        *,
        auth: str | None,
        storage_state: bool | None,
    ) -> dict[str, Any]:
        details = dict(remote_details or {})
        details["auth"] = auth
        details["storage_state"] = storage_state
        details.setdefault("provider", self.settings.provider_mode)
        details.setdefault("ok", self.plugin._provider_error is None)
        return details

    async def get_config(self) -> dict[str, Any]:
        schema = self._load_config_schema()
        editable = EditablePluginConfig(
            values=self._settings_to_editable_values(),
            groups=self._config_groups(),
            schema=schema,
            overlay_path=str(get_runtime_override_path(self.settings.plugin_data_dir)),
        )
        return asdict(editable)

    async def update_config(self, payload: dict[str, Any]) -> dict[str, Any]:
        schema = self._load_config_schema()
        current_values = self._settings_to_editable_values()
        candidate = dict(current_values)
        for key in schema:
            if key in payload:
                candidate[key] = payload[key]
        field_errors = self._validate_config_values(candidate)
        if field_errors:
            return {
                "ok": False,
                "field_errors": field_errors,
            }
        overlay = self._build_runtime_overlay(candidate)
        save_runtime_overrides(self.settings.plugin_data_dir, overlay)
        diff = self._build_config_diff(current_values, candidate)
        return {
            "ok": True,
            "values": candidate,
            "diff": diff,
            "overlay_path": str(get_runtime_override_path(self.settings.plugin_data_dir)),
        }

    async def reload_config(self) -> dict[str, Any]:
        return await self.plugin.reload_runtime()

    def verify_admin_api_key(self, api_key: str) -> bool:
        expected = self.settings.admin_webui_api_key
        return bool(expected) and api_key == expected

    def _normalize_subscription_payload(
        self,
        payload: dict[str, Any],
        *,
        current: Subscription | None = None,
    ) -> dict[str, Any]:
        keyword = str(payload.get("keyword", current.keyword if current else "")).strip()
        umo = str(payload.get("umo", current.umo if current else "")).strip()
        if not keyword:
            raise ValueError("keyword is required")
        if not umo:
            raise ValueError("umo is required")
        interval_sec = int(
            payload.get(
                "interval_sec",
                current.interval_sec if current else self.settings.default_interval_sec,
            )
            or self.settings.default_interval_sec
        )
        pages = int(
            payload.get("pages", current.pages if current else self.settings.default_pages)
            or self.settings.default_pages
        )
        recommend_max_price_raw = payload.get(
            "recommend_max_price",
            current.recommend_max_price if current else None,
        )
        recommend_max_price = (
            float(recommend_max_price_raw)
            if recommend_max_price_raw not in (None, "")
            else None
        )
        drop_abs = float(
            payload.get(
                "drop_abs",
                current.drop_abs if current else self.settings.default_drop_abs,
            )
            or self.settings.default_drop_abs
        )
        drop_pct = float(
            payload.get(
                "drop_pct",
                current.drop_pct if current else self.settings.default_drop_pct,
            )
            or self.settings.default_drop_pct
        )
        new_window_sec = int(
            payload.get(
                "new_window_sec",
                current.new_window_sec if current else self.settings.default_new_window_sec,
            )
            or self.settings.default_new_window_sec
        )
        cooldown_sec = int(
            payload.get(
                "cooldown_sec",
                current.cooldown_sec if current else self.settings.default_cooldown_sec,
            )
            or self.settings.default_cooldown_sec
        )
        price_min = self._normalize_price_bound(
            payload,
            key="price_min",
            current=getattr(current, "price_min", None) if current else None,
        )
        price_max = self._normalize_price_bound(
            payload,
            key="price_max",
            current=getattr(current, "price_max", None) if current else None,
        )
        if price_min is not None and price_max is not None and price_min > price_max:
            raise ValueError("price_min cannot be greater than price_max")
        return {
            "umo": umo,
            "keyword": keyword,
            "interval_sec": max(30, interval_sec),
            "pages": max(1, min(pages, self.settings.max_pages)),
            "recommend_max_price": (
                max(0.0, recommend_max_price)
                if recommend_max_price is not None
                else None
            ),
            "drop_abs": max(0.0, drop_abs),
            "drop_pct": max(0.0, drop_pct),
            "new_window_sec": max(60, new_window_sec),
            "cooldown_sec": max(60, cooldown_sec),
            "price_min": price_min,
            "price_max": price_max,
        }

    @staticmethod
    def _normalize_price_bound(
        payload: dict[str, Any],
        *,
        key: str,
        current: float | None,
    ) -> float | None:
        if key not in payload:
            return current
        raw = payload[key]
        if raw is None or raw == "":
            return None
        try:
            value = float(raw)
        except (TypeError, ValueError):
            return current
        return value if value > 0 else None

    async def _run_manual_subscription_check(self, sub: Subscription) -> dict[str, Any]:
        if self.plugin._provider_error:
            raise RuntimeError(self.plugin._provider_error)
        await self.plugin._ensure_scheduler_started()
        acquired = await self.scheduler.try_acquire_subscription(sub.id)
        if not acquired:
            raise RuntimeError("subscription is already running")
        activity_id = await self.activity_monitor.start_task(
            source="manual_check",
            keyword=sub.keyword,
            umo=sub.umo,
            provider_mode=self.settings.provider_mode,
            page_count=max(1, min(sub.pages, self.settings.max_pages)),
            sub_id=sub.id,
            message="正在抓取闲鱼结果",
        )
        try:
            items = await self.provider.search(
                keyword=sub.keyword,
                pages=max(1, min(sub.pages, self.settings.max_pages)),
                timeout_sec=self.settings.fetch_timeout_sec,
            )
            now_ts = int(time.time())
            await self.activity_monitor.update_task(
                activity_id,
                phase="prefiltering",
                raw_total=len(items),
                message=f"已抓取 {len(items)} 条，正在预筛",
            )
            candidates, filtered_total = await self.scheduler.process_manual_fetch(
                sub=sub,
                items=items,
                now_ts=now_ts,
            )
            await self.activity_monitor.update_task(
                activity_id,
                phase="analyzing",
                filtered_total=filtered_total,
                candidate_total=len(candidates),
                message=(
                    f"已筛出 {len(candidates)} 个候选，正在分析推荐"
                    if candidates
                    else "没有候选商品，正在生成分析结果"
                ),
            )
            recommendation = await self.recommender.analyze(
                umo=sub.umo,
                keyword=sub.keyword,
                candidates=candidates,
                top_k=self.settings.llm_top_k,
                recommend_max_price=sub.recommend_max_price,
            )
            if recommendation.top:
                await self.scheduler.persist_notifications(
                    sub_id=sub.id,
                    candidates=candidates,
                    sent_at=now_ts,
                )
            return self._recommendation_to_payload(
                recommendation=recommendation,
                page_count=sub.pages,
                raw_total=len(items),
                filtered_total=filtered_total,
                filter_mode="SUBSCRIPTION_CHECK",
            )
        finally:
            await self.activity_monitor.finish_task(activity_id)
            await self.scheduler.release_subscription(sub.id)

    async def _run_query(self, *, keyword: str, page_count: int) -> dict[str, Any]:
        if self.plugin._provider_error:
            raise RuntimeError(self.plugin._provider_error)
        activity_id = await self.activity_monitor.start_task(
            source="temporary_query",
            keyword=keyword,
            umo="__admin__",
            provider_mode=self.settings.provider_mode,
            page_count=page_count,
            message="正在抓取闲鱼结果",
        )
        try:
            raw_items = await self.provider.search(
                keyword=keyword,
                pages=page_count,
                timeout_sec=self.settings.fetch_timeout_sec,
            )
            await self.activity_monitor.update_task(
                activity_id,
                phase="prefiltering",
                raw_total=len(raw_items),
                message=f"已抓取 {len(raw_items)} 条，正在预筛",
            )
            filtered_items, filter_mode = await self.recommender.prefilter_items(
                umo="__admin__",
                keyword=keyword,
                items=raw_items,
            )
            candidates = [
                RecommendationCandidate(
                    event_type="NEW",
                    keyword=keyword,
                    item_id=item.item_id,
                    title=item.title,
                    price=item.price,
                    url=item.url,
                    publish_time=item.publish_time,
                    observed_at=int(time.time()),
                )
                for item in filtered_items
            ]
            await self.activity_monitor.update_task(
                activity_id,
                phase="analyzing",
                filtered_total=len(filtered_items),
                candidate_total=len(candidates),
                message=(
                    f"已筛出 {len(candidates)} 个候选，正在分析推荐"
                    if candidates
                    else "没有候选商品，正在生成分析结果"
                ),
            )
            recommendation = await self.recommender.analyze(
                umo="__admin__",
                keyword=keyword,
                candidates=candidates,
                top_k=self.settings.llm_top_k,
            )
            return self._recommendation_to_payload(
                recommendation=recommendation,
                page_count=page_count,
                raw_total=len(raw_items),
                filtered_total=len(filtered_items),
                filter_mode=filter_mode,
            )
        finally:
            await self.activity_monitor.finish_task(activity_id)

    def _recommendation_to_payload(
        self,
        *,
        recommendation: RecommendationResult,
        page_count: int,
        raw_total: int,
        filtered_total: int,
        filter_mode: str,
    ) -> dict[str, Any]:
        preview = QueryPreview(
            keyword=recommendation.keyword,
            page_count=page_count,
            raw_total=raw_total,
            filtered_total=filtered_total,
            filter_mode=filter_mode,
            summary=recommendation.summary,
            used_llm=recommendation.used_llm,
            fallback_reason=recommendation.fallback_reason,
            items=[
                QueryPreviewItem(
                    item_id=item.item_id,
                    title=item.title,
                    price=item.price,
                    url=item.url,
                    score=item.score,
                    reason=item.reason,
                    risk=item.risk,
                )
                for item in recommendation.top
            ],
        )
        return asdict(preview)

    def _to_subscription_summary(self, sub: Subscription) -> SubscriptionSummary:
        return SubscriptionSummary(
            id=sub.id,
            umo=sub.umo,
            keyword=sub.keyword,
            interval_sec=sub.interval_sec,
            pages=sub.pages,
            recommend_max_price=sub.recommend_max_price,
            drop_abs=sub.drop_abs,
            drop_pct=sub.drop_pct,
            new_window_sec=sub.new_window_sec,
            cooldown_sec=sub.cooldown_sec,
            enabled=sub.enabled,
            paused_reason=sub.paused_reason,
            last_run_at=sub.last_run_at,
            next_run_at=sub.next_run_at,
            consecutive_failures=sub.consecutive_failures,
            price_min=sub.price_min,
            price_max=sub.price_max,
        )

    def _settings_to_editable_values(self) -> dict[str, Any]:
        settings = self.settings
        return {
            "provider_mode": settings.provider_mode,
            "remote_base_url": settings.remote_base_url or "",
            "remote_headers": self._remote_headers_to_list(settings.remote_headers_json),
            "remote_api_key": settings.remote_api_key or "",
            "remote_timeout_sec": settings.remote_timeout_sec,
            "remote_healthcheck_on_init": settings.remote_healthcheck_on_init,
            "remote_healthcheck_timeout_sec": settings.remote_healthcheck_timeout_sec,
            "playwright_executable_path": str(settings.playwright_executable_path or ""),
            "playwright_block_assets": settings.playwright_block_assets,
            "playwright_force_direct": settings.playwright_force_direct,
            "default_interval_sec": settings.default_interval_sec,
            "default_pages": settings.default_pages,
            "max_pages": settings.max_pages,
            "scheduler_tick_sec": settings.scheduler_tick_sec,
            "max_concurrency": settings.max_concurrency,
            "queue_max_size": settings.queue_max_size,
            "fetch_timeout_sec": settings.fetch_timeout_sec,
            "max_retries": settings.max_retries,
            "retry_base_sec": settings.retry_base_sec,
            "retry_max_sec": settings.retry_max_sec,
            "default_new_window_sec": settings.default_new_window_sec,
            "default_drop_abs": settings.default_drop_abs,
            "default_drop_pct": settings.default_drop_pct,
            "default_cooldown_sec": settings.default_cooldown_sec,
            "webhook_url": settings.webhook_url or "",
            "llm_enabled": settings.llm_enabled,
            "llm_provider_id": settings.llm_provider_id or "",
            "llm_prefilter_provider_id": settings.llm_prefilter_provider_id or "",
            "llm_timeout_sec": settings.llm_timeout_sec,
            "llm_top_k": settings.llm_top_k,
            "llm_min_score": settings.llm_min_score,
            "llm_max_candidates": settings.llm_max_candidates,
            "llm_recommend_prompt": settings.llm_recommend_prompt,
            "llm_prefilter_enabled": settings.llm_prefilter_enabled,
            "llm_prefilter_timeout_sec": settings.llm_prefilter_timeout_sec,
            "llm_prefilter_max_items": settings.llm_prefilter_max_items,
            "llm_prefilter_prompt": settings.llm_prefilter_prompt,
            "llm_agent_enabled": settings.llm_agent_enabled,
            "llm_agent_provider_id": settings.llm_agent_provider_id or "",
            "llm_agent_headless": settings.llm_agent_headless,
            "llm_agent_max_concurrent": settings.llm_agent_max_concurrent,
            "llm_agent_step_timeout_sec": settings.llm_agent_step_timeout_sec,
            "admin_webui_enabled": settings.admin_webui_enabled,
            "admin_webui_host": settings.admin_webui_host or DEFAULT_ADMIN_WEBUI_HOST,
            "admin_webui_port": settings.admin_webui_port or DEFAULT_ADMIN_WEBUI_PORT,
            "admin_webui_api_key": settings.admin_webui_api_key or "",
        }

    def _validate_config_values(self, values: dict[str, Any]) -> dict[str, str]:
        errors: dict[str, str] = {}
        provider_mode = str(values.get("provider_mode", "")).strip()
        if provider_mode not in {"playwright_local", "remote_rest"}:
            errors["provider_mode"] = "仅支持 playwright_local 或 remote_rest"
        if provider_mode == "remote_rest" and not str(values.get("remote_base_url", "")).strip():
            errors["remote_base_url"] = "remote_rest 模式必须填写远程地址"
        if int(values.get("default_pages", 1) or 1) > int(values.get("max_pages", 1) or 1):
            errors["default_pages"] = "默认页数不能大于最大页数"
        if int(values.get("admin_webui_port", DEFAULT_ADMIN_WEBUI_PORT) or DEFAULT_ADMIN_WEBUI_PORT) < 1:
            errors["admin_webui_port"] = "端口必须大于 0"
        if not str(values.get("admin_webui_host", "")).strip():
            errors["admin_webui_host"] = "后台监听地址不能为空"
        if bool(values.get("admin_webui_enabled")) and not str(values.get("admin_webui_api_key", "")).strip():
            errors["admin_webui_api_key"] = "启用后台时必须配置 API Key"
        try:
            load_plugin_settings(
                values,
                self.settings.plugin_name,
                self.settings.plugin_data_dir,
            )
        except Exception as exc:
            message = str(exc)
            target = "config"
            if "playwright_executable_path" in message:
                target = "playwright_executable_path"
            elif "remote_headers_json" in message:
                target = "remote_headers"
            errors[target] = message
        return errors

    def _build_runtime_overlay(self, values: dict[str, Any]) -> dict[str, Any]:
        overlay: dict[str, Any] = {}
        for key, value in values.items():
            if key == "remote_headers":
                overlay[key] = [str(item) for item in value or [] if str(item).strip()]
                continue
            overlay[key] = value
        return overlay

    def _build_config_diff(
        self,
        current_values: dict[str, Any],
        next_values: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        diff: dict[str, dict[str, Any]] = {}
        for key, old_value in current_values.items():
            new_value = next_values.get(key)
            if new_value != old_value:
                diff[key] = {"old": old_value, "new": new_value}
        return diff

    def _load_config_schema(self) -> dict[str, Any]:
        if self._config_schema_cache is not None:
            return self._config_schema_cache
        schema_path = Path(__file__).resolve().parent / "_admin_schema.json"
        self._config_schema_cache = json.loads(schema_path.read_text(encoding="utf-8"))
        return self._config_schema_cache

    def _config_groups(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "provider",
                "title": "抓取模式",
                "fields": [
                    "provider_mode",
                    "playwright_executable_path",
                    "playwright_block_assets",
                    "playwright_force_direct",
                ],
            },
            {
                "id": "remote",
                "title": "远程 Worker",
                "fields": [
                    "remote_base_url",
                    "remote_headers",
                    "remote_api_key",
                    "remote_timeout_sec",
                    "remote_healthcheck_on_init",
                    "remote_healthcheck_timeout_sec",
                ],
            },
            {
                "id": "scheduler",
                "title": "调度与重试",
                "fields": [
                    "default_interval_sec",
                    "default_pages",
                    "max_pages",
                    "scheduler_tick_sec",
                    "max_concurrency",
                    "queue_max_size",
                    "fetch_timeout_sec",
                    "max_retries",
                    "retry_base_sec",
                    "retry_max_sec",
                ],
            },
            {
                "id": "events",
                "title": "事件阈值",
                "fields": [
                    "default_new_window_sec",
                    "default_drop_abs",
                    "default_drop_pct",
                    "default_cooldown_sec",
                ],
            },
            {
                "id": "llm",
                "title": "LLM 推荐",
                "fields": [
                    "llm_enabled",
                    "llm_provider_id",
                    "llm_prefilter_provider_id",
                    "llm_timeout_sec",
                    "llm_top_k",
                    "llm_min_score",
                    "llm_max_candidates",
                    "llm_recommend_prompt",
                    "llm_prefilter_enabled",
                    "llm_prefilter_timeout_sec",
                    "llm_prefilter_max_items",
                    "llm_prefilter_prompt",
                ],
            },
            {
                "id": "notify",
                "title": "通知与 Webhook",
                "fields": ["webhook_url"],
            },
            {
                "id": "agent",
                "title": "浏览器 Agent",
                "fields": [
                    "llm_agent_enabled",
                    "llm_agent_provider_id",
                    "llm_agent_headless",
                    "llm_agent_max_concurrent",
                    "llm_agent_step_timeout_sec",
                ],
            },
            {
                "id": "admin",
                "title": "管理后台",
                "fields": [
                    "admin_webui_enabled",
                    "admin_webui_host",
                    "admin_webui_port",
                    "admin_webui_api_key",
                ],
            },
        ]

    def _remote_headers_to_list(self, raw_json: str | None) -> list[str]:
        if not raw_json:
            return []
        try:
            payload = json.loads(raw_json)
        except json.JSONDecodeError:
            return []
        if not isinstance(payload, dict):
            return []
        return [f"{key}: {value}" for key, value in payload.items() if str(key).strip()]
