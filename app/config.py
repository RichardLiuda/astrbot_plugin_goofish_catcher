from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from astrbot.api import logger

PROVIDER_MODE_PLAYWRIGHT_LOCAL = "playwright_local"
PROVIDER_MODE_REMOTE_REST = "remote_rest"
SUPPORTED_PROVIDER_MODES = {
    PROVIDER_MODE_PLAYWRIGHT_LOCAL,
    PROVIDER_MODE_REMOTE_REST,
}


def _as_int(value: Any, default: int) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_float(value: Any, default: float) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "on"}:
            return True
        if lowered in {"false", "0", "no", "off"}:
            return False
    return default


def _first_file(raw_value: Any) -> str | None:
    if isinstance(raw_value, list) and raw_value:
        first = raw_value[0]
        return str(first) if first else None
    if isinstance(raw_value, str) and raw_value.strip():
        return raw_value.strip()
    return None


@dataclass(slots=True)
class PluginSettings:
    plugin_name: str
    plugin_data_dir: Path
    db_path: Path
    provider_mode: str
    default_interval_sec: int
    default_pages: int
    max_pages: int
    scheduler_tick_sec: int
    max_concurrency: int
    fetch_timeout_sec: int
    max_retries: int
    retry_base_sec: int
    retry_max_sec: int
    default_new_window_sec: int
    default_drop_abs: float
    default_drop_pct: float
    default_cooldown_sec: int
    playwright_storage_state_path: Path | None
    playwright_headless: bool
    playwright_block_assets: bool
    webhook_url: str | None
    remote_base_url: str | None
    remote_api_key: str | None
    remote_timeout_sec: int
    queue_max_size: int
    llm_enabled: bool
    llm_provider_id: str | None
    llm_prefilter_provider_id: str | None
    llm_timeout_sec: int
    llm_top_k: int
    llm_max_candidates: int
    llm_prefilter_enabled: bool
    llm_prefilter_timeout_sec: int
    llm_prefilter_max_items: int


def load_plugin_settings(
    config: dict[str, Any] | None,
    plugin_name: str,
    plugin_data_dir: Path | None = None,
) -> PluginSettings:
    raw = dict(config or {})

    resolved_data_dir = plugin_data_dir
    if resolved_data_dir is None:
        # Compatibility fallback for callers that do not inject StarTools data dir.
        from astrbot.core.utils.astrbot_path import get_astrbot_plugin_data_path

        resolved_data_dir = Path(get_astrbot_plugin_data_path()) / plugin_name

    plugin_data_dir = Path(resolved_data_dir)
    plugin_data_dir.mkdir(parents=True, exist_ok=True)
    db_path = plugin_data_dir / "goofish_catcher.db"

    requested_provider_mode = str(
        raw.get("provider_mode", PROVIDER_MODE_PLAYWRIGHT_LOCAL)
    ).strip()
    provider_mode = PROVIDER_MODE_PLAYWRIGHT_LOCAL
    if requested_provider_mode and requested_provider_mode != provider_mode:
        logger.info(
            "[%s] provider_mode=%s is temporarily disabled, forced to %s",
            plugin_name,
            requested_provider_mode,
            provider_mode,
        )

    storage_state_path: Path | None = None
    storage_state_file = _first_file(raw.get("playwright_storage_state_file"))
    if storage_state_file:
        candidate = Path(storage_state_file)
        if not candidate.is_absolute():
            candidate = plugin_data_dir / storage_state_file
        if candidate.exists():
            storage_state_path = candidate
        else:
            logger.warning(
                "[%s] playwright_storage_state_file not found: %s",
                plugin_name,
                candidate,
            )

    webhook_url = str(raw.get("webhook_url", "")).strip() or None
    remote_base_url = None
    remote_api_key = None
    llm_provider_id = str(raw.get("llm_provider_id", "")).strip() or None
    llm_prefilter_provider_id = (
        str(raw.get("llm_prefilter_provider_id", "")).strip() or None
    )

    default_interval_sec = max(30, _as_int(raw.get("default_interval_sec"), 600))
    default_pages = max(1, _as_int(raw.get("default_pages"), 1))
    max_pages = max(1, _as_int(raw.get("max_pages"), 2))
    if default_pages > max_pages:
        default_pages = max_pages

    return PluginSettings(
        plugin_name=plugin_name,
        plugin_data_dir=plugin_data_dir,
        db_path=db_path,
        provider_mode=provider_mode,
        default_interval_sec=default_interval_sec,
        default_pages=default_pages,
        max_pages=max_pages,
        scheduler_tick_sec=max(5, _as_int(raw.get("scheduler_tick_sec"), 15)),
        max_concurrency=max(1, _as_int(raw.get("max_concurrency"), 1)),
        fetch_timeout_sec=max(5, _as_int(raw.get("fetch_timeout_sec"), 20)),
        max_retries=max(0, _as_int(raw.get("max_retries"), 3)),
        retry_base_sec=max(1, _as_int(raw.get("retry_base_sec"), 30)),
        retry_max_sec=max(5, _as_int(raw.get("retry_max_sec"), 900)),
        default_new_window_sec=max(
            60, _as_int(raw.get("default_new_window_sec"), 1800)
        ),
        default_drop_abs=max(0.0, _as_float(raw.get("default_drop_abs"), 50.0)),
        default_drop_pct=max(0.0, _as_float(raw.get("default_drop_pct"), 0.05)),
        default_cooldown_sec=max(60, _as_int(raw.get("default_cooldown_sec"), 21600)),
        playwright_storage_state_path=storage_state_path,
        playwright_headless=False,
        playwright_block_assets=_as_bool(raw.get("playwright_block_assets"), True),
        webhook_url=webhook_url,
        remote_base_url=remote_base_url,
        remote_api_key=remote_api_key,
        remote_timeout_sec=20,
        queue_max_size=max(10, _as_int(raw.get("queue_max_size"), 256)),
        llm_enabled=_as_bool(raw.get("llm_enabled"), True),
        llm_provider_id=llm_provider_id,
        llm_prefilter_provider_id=llm_prefilter_provider_id,
        llm_timeout_sec=max(5, _as_int(raw.get("llm_timeout_sec"), 25)),
        llm_top_k=max(1, _as_int(raw.get("llm_top_k"), 3)),
        llm_max_candidates=max(1, _as_int(raw.get("llm_max_candidates"), 20)),
        llm_prefilter_enabled=_as_bool(raw.get("llm_prefilter_enabled"), True),
        llm_prefilter_timeout_sec=max(
            1, _as_int(raw.get("llm_prefilter_timeout_sec"), 6)
        ),
        llm_prefilter_max_items=max(1, _as_int(raw.get("llm_prefilter_max_items"), 30)),
    )
