from __future__ import annotations

import json
import shutil
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from astrbot.api import logger
except ModuleNotFoundError:
    logger = logging.getLogger("astrbot_plugin_goofish_catcher")

PROVIDER_MODE_PLAYWRIGHT_LOCAL = "playwright_local"
PROVIDER_MODE_REMOTE_REST = "remote_rest"
SUPPORTED_PROVIDER_MODES = {
    PROVIDER_MODE_PLAYWRIGHT_LOCAL,
    PROVIDER_MODE_REMOTE_REST,
}
ADMIN_RUNTIME_CONFIG_NAME = "admin_runtime_config.json"
DEFAULT_ADMIN_WEBUI_HOST = "127.0.0.1"
DEFAULT_ADMIN_WEBUI_PORT = 8790

DEFAULT_LLM_RECOMMEND_PROMPT = (
    "关键词: $keyword\n"
    "候选条目（最多推荐 $top_k 条）:\n"
    "$candidates_json\n\n"
    "请优先保证结果真正符合条件，宁缺毋滥，不要为了凑满 $top_k 而强行推荐。"
    "如果只有少量条目符合条件，可以少于 $top_k 条；如果没有任何条目符合条件，可以返回 0 条。"
    "请输出 JSON，字段必须包含 summary 和 top。"
)

DEFAULT_LLM_PREFILTER_PROMPT = (
    "关键词: $keyword\n"
    "商品列表: $items_json\n"
    "请只做“商品相关性筛选”，忽略价格、功能优劣、成色。\n"
    '输出 JSON: {"keep_item_ids": ["..."]}'
)


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


def _as_optional_path(value: Any) -> Path | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return Path(text).expanduser()


def _first_file(raw_value: Any) -> str | None:
    if isinstance(raw_value, list) and raw_value:
        first = raw_value[0]
        return str(first) if first else None
    if isinstance(raw_value, str) and raw_value.strip():
        return raw_value.strip()
    return None


def _normalize_remote_headers(
    raw: dict[str, Any],
    *,
    plugin_name: str,
) -> str | None:
    raw_json = str(raw.get("remote_headers_json", "")).strip() or None
    if raw_json:
        return raw_json

    raw_list = raw.get("remote_headers")
    if raw_list is None:
        return None
    if not isinstance(raw_list, list):
        logger.warning(
            "[%s] remote_headers should be a list, got %s",
            plugin_name,
            type(raw_list).__name__,
        )
        return None

    headers: dict[str, str] = {}
    for item in raw_list:
        text = str(item).strip()
        if not text:
            continue
        key, sep, value = text.partition(":")
        if not sep:
            logger.warning(
                "[%s] ignore invalid remote_headers item without colon: %s",
                plugin_name,
                text,
            )
            continue
        key_text = key.strip()
        value_text = value.strip()
        if not key_text or not value_text:
            logger.warning(
                "[%s] ignore invalid remote_headers item with empty key/value: %s",
                plugin_name,
                text,
            )
            continue
        headers[key_text] = value_text

    if not headers:
        return None
    return json.dumps(headers, ensure_ascii=False)


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
    playwright_executable_path: Path | None
    playwright_headless: bool
    playwright_block_assets: bool
    playwright_force_direct: bool
    webhook_url: str | None
    remote_base_url: str | None
    remote_api_key: str | None
    remote_headers_json: str | None
    remote_timeout_sec: int
    remote_healthcheck_on_init: bool
    remote_healthcheck_timeout_sec: int
    queue_max_size: int
    llm_enabled: bool
    llm_provider_id: str | None
    llm_prefilter_provider_id: str | None
    llm_timeout_sec: int = 25
    llm_top_k: int = 3
    llm_min_score: float = 0.0
    llm_max_candidates: int = 20
    llm_prefilter_enabled: bool = True
    llm_prefilter_timeout_sec: int = 6
    llm_prefilter_max_items: int = 30
    llm_recommend_prompt: str = DEFAULT_LLM_RECOMMEND_PROMPT
    llm_prefilter_prompt: str = DEFAULT_LLM_PREFILTER_PROMPT
    admin_webui_enabled: bool = False
    admin_webui_host: str = DEFAULT_ADMIN_WEBUI_HOST
    admin_webui_port: int = DEFAULT_ADMIN_WEBUI_PORT
    admin_webui_api_key: str | None = None


def get_runtime_override_path(plugin_data_dir: Path) -> Path:
    return Path(plugin_data_dir) / ADMIN_RUNTIME_CONFIG_NAME


def load_runtime_overrides(plugin_data_dir: Path) -> dict[str, Any]:
    path = get_runtime_override_path(plugin_data_dir)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.error(
            "[goofish_catcher] failed to load admin runtime config %s: %s",
            path,
            exc,
        )
        return {}
    if not isinstance(payload, dict):
        logger.error(
            "[goofish_catcher] ignore admin runtime config %s because root is not an object",
            path,
        )
        return {}
    return payload


def save_runtime_overrides(plugin_data_dir: Path, overrides: dict[str, Any]) -> Path:
    path = get_runtime_override_path(plugin_data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(overrides, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def load_effective_raw_config(
    config: dict[str, Any] | None,
    plugin_data_dir: Path,
) -> dict[str, Any]:
    raw = dict(config or {})
    raw.update(load_runtime_overrides(plugin_data_dir))
    return raw


def load_plugin_settings(
    config: dict[str, Any] | None,
    plugin_name: str,
    plugin_data_dir: Path,
) -> PluginSettings:
    plugin_data_dir = Path(plugin_data_dir)
    plugin_data_dir.mkdir(parents=True, exist_ok=True)
    raw = load_effective_raw_config(config, plugin_data_dir)
    db_path = plugin_data_dir / "goofish_catcher.db"

    requested_provider_mode = str(
        raw.get("provider_mode", PROVIDER_MODE_PLAYWRIGHT_LOCAL)
    ).strip()
    provider_mode = requested_provider_mode or PROVIDER_MODE_PLAYWRIGHT_LOCAL
    if provider_mode not in SUPPORTED_PROVIDER_MODES:
        logger.warning(
            "[%s] unsupported provider_mode=%s, fallback to %s",
            plugin_name,
            provider_mode,
            PROVIDER_MODE_PLAYWRIGHT_LOCAL,
        )
        provider_mode = PROVIDER_MODE_PLAYWRIGHT_LOCAL

    storage_state_path: Path | None = None
    stable_state_path = plugin_data_dir / "storage_state.json"
    storage_state_file = _first_file(raw.get("playwright_storage_state_file"))
    if storage_state_file:
        candidate = Path(storage_state_file)
        if not candidate.is_absolute():
            candidate = plugin_data_dir / storage_state_file
        if candidate.exists():
            try:
                # Keep a stable state copy under plugin data dir to survive temp-file cleanup.
                if candidate.resolve() != stable_state_path.resolve():
                    shutil.copy2(candidate, stable_state_path)
                    logger.info(
                        "[%s] copied playwright storage_state to stable path: %s",
                        plugin_name,
                        stable_state_path,
                    )
                storage_state_path = stable_state_path
            except Exception as exc:
                logger.warning(
                    "[%s] failed to copy storage_state from %s to %s: %s",
                    plugin_name,
                    candidate,
                    stable_state_path,
                    exc,
                )
                storage_state_path = candidate
        else:
            logger.warning(
                "[%s] playwright_storage_state_file not found: %s",
                plugin_name,
                candidate,
            )
    if storage_state_path is None and stable_state_path.exists():
        storage_state_path = stable_state_path
        logger.info(
            "[%s] use fallback playwright storage_state from stable path: %s",
            plugin_name,
            stable_state_path,
        )

    webhook_url = str(raw.get("webhook_url", "")).strip() or None
    remote_base_url = str(raw.get("remote_base_url", "")).strip() or None
    remote_api_key = str(raw.get("remote_api_key", "")).strip() or None
    playwright_executable_path = _as_optional_path(
        raw.get("playwright_executable_path")
    )
    remote_headers_json = _normalize_remote_headers(raw, plugin_name=plugin_name)
    llm_provider_id = str(raw.get("llm_provider_id", "")).strip() or None
    llm_prefilter_provider_id = (
        str(raw.get("llm_prefilter_provider_id", "")).strip() or None
    )
    llm_recommend_prompt = (
        str(raw.get("llm_recommend_prompt", "")).strip()
        or DEFAULT_LLM_RECOMMEND_PROMPT
    )
    llm_prefilter_prompt = (
        str(raw.get("llm_prefilter_prompt", "")).strip()
        or DEFAULT_LLM_PREFILTER_PROMPT
    )
    admin_webui_host = (
        str(raw.get("admin_webui_host", DEFAULT_ADMIN_WEBUI_HOST)).strip()
        or DEFAULT_ADMIN_WEBUI_HOST
    )
    admin_webui_api_key = str(raw.get("admin_webui_api_key", "")).strip() or None
    admin_webui_port = max(
        1,
        min(65535, _as_int(raw.get("admin_webui_port"), DEFAULT_ADMIN_WEBUI_PORT)),
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
        playwright_executable_path=playwright_executable_path,
        playwright_headless=False,
        playwright_block_assets=_as_bool(raw.get("playwright_block_assets"), True),
        playwright_force_direct=_as_bool(raw.get("playwright_force_direct"), True),
        webhook_url=webhook_url,
        remote_base_url=remote_base_url,
        remote_api_key=remote_api_key,
        remote_headers_json=remote_headers_json,
        remote_timeout_sec=max(1, _as_int(raw.get("remote_timeout_sec"), 20)),
        remote_healthcheck_on_init=_as_bool(
            raw.get("remote_healthcheck_on_init"),
            True,
        ),
        remote_healthcheck_timeout_sec=max(
            1,
            _as_int(raw.get("remote_healthcheck_timeout_sec"), 10),
        ),
        queue_max_size=max(10, _as_int(raw.get("queue_max_size"), 256)),
        llm_enabled=_as_bool(raw.get("llm_enabled"), True),
        llm_provider_id=llm_provider_id,
        llm_prefilter_provider_id=llm_prefilter_provider_id,
        llm_timeout_sec=max(5, _as_int(raw.get("llm_timeout_sec"), 25)),
        llm_top_k=max(1, _as_int(raw.get("llm_top_k"), 3)),
        llm_min_score=max(0.0, min(100.0, _as_float(raw.get("llm_min_score"), 0.0))),
        llm_max_candidates=max(1, _as_int(raw.get("llm_max_candidates"), 20)),
        llm_recommend_prompt=llm_recommend_prompt,
        llm_prefilter_enabled=_as_bool(raw.get("llm_prefilter_enabled"), True),
        llm_prefilter_timeout_sec=max(
            1, _as_int(raw.get("llm_prefilter_timeout_sec"), 6)
        ),
        llm_prefilter_max_items=max(1, _as_int(raw.get("llm_prefilter_max_items"), 30)),
        llm_prefilter_prompt=llm_prefilter_prompt,
        admin_webui_enabled=_as_bool(raw.get("admin_webui_enabled"), False),
        admin_webui_host=admin_webui_host,
        admin_webui_port=admin_webui_port,
        admin_webui_api_key=admin_webui_api_key,
    )
