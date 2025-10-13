"""Metric similarity helpers backed by optional FAISS indexes."""
from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence

try:  # pragma: no cover - optional dependency
    import faiss  # type: ignore
except Exception:  # pragma: no cover - faiss is optional at runtime
    faiss = None  # type: ignore

try:  # pragma: no cover - numpy is optional in some environments
    import numpy as np
except Exception:  # pragma: no cover - numpy might be unavailable
    np = None  # type: ignore

TOKEN_RE = re.compile(r"[\w']+")


@dataclass(frozen=True)
class MetricDocument:
    """A lightweight representation of a metric for similarity search."""

    key: str
    text: str
    summary: str
    metadata: Dict[str, Any]


class HashingEmbedder:
    """Project text into a deterministic dense vector space.

    The embedder purposely avoids external APIs so that we can build the FAISS
    index during request handling without extra network calls.  It hashes each
    token into a fixed number of buckets and then L2 normalises the vector so
    that inner-product search matches cosine similarity.
    """

    def __init__(self, dimensions: int = 256):
        self.dimensions = max(dimensions, 64)

    def embed(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimensions

        vector = [0.0] * self.dimensions
        for token in TOKEN_RE.findall(text.lower()):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[idx] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm:
            vector = [value / norm for value in vector]
        return vector


class MetricSimilarityIndex:
    """Perform semantic similarity search over metric metadata."""

    def __init__(self, metrics: Sequence[Any], *, embedder: Optional[HashingEmbedder] = None):
        self.metrics = list(metrics)
        self.embedder = embedder or HashingEmbedder()
        self.documents: List[MetricDocument] = list(self._build_documents(self.metrics))
        self._vectors: List[List[float]] = [self.embedder.embed(doc.text) for doc in self.documents]
        self._faiss_index = self._build_faiss_index()

    # Public API ---------------------------------------------------------
    def search(self, query: str, *, top_k: int = 5) -> List[MetricDocument]:
        if not query or not query.strip():
            return []
        if not self.documents:
            return []

        vector = self.embedder.embed(query)
        k = min(max(top_k, 1), len(self.documents))

        if self._faiss_index is not None:
            scores, indices = self._faiss_index.search(self._as_matrix([vector]), k)
            ranked = [self.documents[idx] for idx in indices[0] if idx >= 0]
        else:
            ranked = self._fallback_rank(vector, k)
        return ranked

    def build_context(self, query: str, *, top_k: int = 5) -> str:
        """Return a human readable bullet list describing likely metrics."""

        results = self.search(query, top_k=top_k)
        if not results:
            return ""

        lines = ["Potentially relevant metrics based on semantic similarity:"]
        for doc in results:
            label = doc.metadata.get("label", doc.key)
            lines.append(f"- {doc.key} ({label}): {doc.summary}")
        return "\n".join(lines)

    def best_match(self, query: str) -> Optional[MetricDocument]:
        matches = self.search(query, top_k=1)
        return matches[0] if matches else None

    # Internals ----------------------------------------------------------
    def _build_documents(self, metrics: Iterable[Any]) -> Iterable[MetricDocument]:
        for metric in metrics:
            key = getattr(metric, "key", "")
            label = getattr(metric, "label", key)
            description = (getattr(metric, "description", "") or "").strip()
            breakdowns = ", ".join(
                b for b in (getattr(metric, "allowed_breakdowns", []) or []) if b and b != "none"
            )
            filters = ", ".join(getattr(metric, "allowed_filters", []) or [])
            tags = ", ".join(getattr(metric, "tags", []) or [])

            pieces = [label]
            if description:
                pieces.append(description)
            if breakdowns:
                pieces.append(f"Breakdowns: {breakdowns}.")
            if filters:
                pieces.append(f"Filters: {filters}.")
            if tags:
                pieces.append(f"Tags: {tags}.")

            text = " ".join(piece for piece in pieces if piece)
            summary = description.split(".")[0].strip() if description else label
            metadata = {
                "metric_key": key,
                "label": label,
                "breakdowns": breakdowns,
                "filters": filters,
            }
            yield MetricDocument(key=key, text=text, summary=summary or label, metadata=metadata)

    def _build_faiss_index(self):  # pragma: no cover - requires optional deps
        if not self._vectors:
            return None
        if faiss is None or np is None:
            return None

        matrix = self._as_matrix(self._vectors)
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        return index

    def _as_matrix(self, vectors: Sequence[Sequence[float]]):  # pragma: no cover - depends on numpy
        if np is None:
            raise RuntimeError("NumPy is required to build a FAISS index")
        return np.array(vectors, dtype="float32")

    def _fallback_rank(self, vector: Sequence[float], top_k: int) -> List[MetricDocument]:
        scores = []
        for idx, candidate in enumerate(self._vectors):
            score = sum(a * b for a, b in zip(vector, candidate))
            scores.append((score, idx))
        scores.sort(key=lambda item: item[0], reverse=True)
        return [self.documents[idx] for _, idx in scores[:top_k]]
