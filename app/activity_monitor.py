from __future__ import annotations

import asyncio
import time
from dataclasses import asdict, dataclass
from typing import Any


_PHASE_ORDER = {
    "fetching": 1,
    "prefiltering": 2,
    "analyzing": 3,
}

_PHASE_LABELS = {
    "fetching": "抓取中",
    "prefiltering": "预筛中",
    "analyzing": "分析中",
}

_SOURCE_LABELS = {
    "subscription": "订阅检查",
    "manual_check": "手动检查",
    "temporary_query": "临时查询",
}


@dataclass(slots=True)
class ActivityTask:
    task_id: str
    source: str
    source_label: str
    phase: str
    phase_label: str
    keyword: str
    umo: str | None
    provider_mode: str
    page_count: int
    started_at: int
    updated_at: int
    sub_id: int | None = None
    worker_idx: int | None = None
    raw_total: int | None = None
    filtered_total: int | None = None
    candidate_total: int | None = None
    message: str | None = None
    total_steps: int = 3
    current_step: int = 1

    @property
    def progress_pct(self) -> int:
        total_steps = max(1, self.total_steps)
        current_step = max(1, min(self.current_step, total_steps))
        return int(current_step / total_steps * 100)


class ActivityMonitor:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._tasks: dict[str, ActivityTask] = {}
        self._seq = 0

    async def start_task(
        self,
        *,
        source: str,
        keyword: str,
        provider_mode: str,
        page_count: int,
        umo: str | None = None,
        sub_id: int | None = None,
        worker_idx: int | None = None,
        message: str | None = None,
    ) -> str:
        async with self._lock:
            self._seq += 1
            now_ts = int(time.time())
            task_id = f"task-{now_ts}-{self._seq}"
            task = ActivityTask(
                task_id=task_id,
                source=source,
                source_label=_SOURCE_LABELS.get(source, source),
                phase="fetching",
                phase_label=_PHASE_LABELS["fetching"],
                keyword=keyword,
                umo=umo,
                provider_mode=provider_mode,
                page_count=page_count,
                started_at=now_ts,
                updated_at=now_ts,
                sub_id=sub_id,
                worker_idx=worker_idx,
                message=message,
                current_step=_PHASE_ORDER["fetching"],
            )
            self._tasks[task_id] = task
            return task_id

    async def update_task(
        self,
        task_id: str,
        *,
        phase: str | None = None,
        raw_total: int | None = None,
        filtered_total: int | None = None,
        candidate_total: int | None = None,
        message: str | None = None,
    ) -> None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return
            if phase:
                task.phase = phase
                task.phase_label = _PHASE_LABELS.get(phase, phase)
                task.current_step = _PHASE_ORDER.get(phase, task.current_step)
            if raw_total is not None:
                task.raw_total = raw_total
            if filtered_total is not None:
                task.filtered_total = filtered_total
            if candidate_total is not None:
                task.candidate_total = candidate_total
            if message is not None:
                task.message = message
            task.updated_at = int(time.time())

    async def finish_task(self, task_id: str) -> None:
        async with self._lock:
            self._tasks.pop(task_id, None)

    async def snapshot(self) -> dict[str, Any]:
        async with self._lock:
            tasks = sorted(
                self._tasks.values(),
                key=lambda item: (item.started_at, item.task_id),
                reverse=True,
            )
            items = [
                {
                    **asdict(task),
                    "progress_pct": task.progress_pct,
                }
                for task in tasks
            ]

        phase_counts = {
            "fetching": 0,
            "prefiltering": 0,
            "analyzing": 0,
        }
        for item in items:
            phase = str(item.get("phase") or "")
            if phase in phase_counts:
                phase_counts[phase] += 1

        return {
            "items": items,
            "summary": {
                "active_count": len(items),
                "fetching_count": phase_counts["fetching"],
                "prefiltering_count": phase_counts["prefiltering"],
                "analyzing_count": phase_counts["analyzing"],
                "updated_at": int(time.time()),
            },
        }
