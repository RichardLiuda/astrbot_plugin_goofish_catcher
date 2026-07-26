"""聚合层（阶段 2.x）：去重 / 风险打标 / 评分 / 排序。"""

from .aggregate import DecisionItem, dedupe_items, rank_items, risk_tags_for, score_heuristic

__all__ = [
    "DecisionItem",
    "dedupe_items",
    "rank_items",
    "risk_tags_for",
    "score_heuristic",
]
