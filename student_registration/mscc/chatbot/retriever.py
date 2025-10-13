"""Similarity-based retrieval helpers for the BMA chatbot."""
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

try:  # pragma: no cover - optional dependency
    import numpy as np
except Exception:  # pragma: no cover - numpy might be unavailable
    np = None  # type: ignore


TOKEN_RE = re.compile(r"[\w']+")


@dataclass(frozen=True)
class InsightDocument:
    """Container for a single insight that can be searched."""

    text: str
    metadata: Dict[str, Any]


class HashingEmbedder:
    """Create deterministic dense vectors for text snippets.

    The embedder uses a simple hashing trick to project tokens into a fixed
    dimensional space.  It is intentionally lightweight so that it works in the
    constrained execution environment used by the kata while still providing a
    vector representation that FAISS (when available) can index.
    """

    def __init__(self, dimensions: int = 256):
        self.dimensions = max(dimensions, 32)

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


class BMAInsightsRetriever:
    """Perform semantic searches over a snapshot of BMA metrics.

    The retriever converts a snapshot produced by :class:`BMAInsightsRepository`
    into a series of concise textual documents.  These documents capture the key
    metrics (totals, break-downs, monthly trends, and the most recent
    registrations).  Each user question is embedded using :class:`HashingEmbedder`
    and compared to the stored documents.  When FAISS is available we rely on it
    for efficient similarity search; otherwise, a deterministic cosine-similarity
    fallback keeps the behaviour functional.
    """

    def __init__(self, snapshot: Dict[str, Any], *, embedder: Optional[HashingEmbedder] = None):
        self.snapshot = snapshot
        self.embedder = embedder or HashingEmbedder()
        self.documents: List[InsightDocument] = list(self._build_documents(snapshot))
        self._vectors: List[List[float]] = [self.embedder.embed(doc.text) for doc in self.documents]
        self._faiss_index = self._build_faiss_index()

    # Public API -------------------------------------------------------------
    def build_context(self, question: str, *, top_k: int = 5) -> str:
        """Return a Markdown bullet list with the most relevant insights."""

        results = self.search(question, top_k=top_k)
        if not results:
            return ""

        lines = []
        for document in results:
            category = document.metadata.get("category", "metric")
            label = document.metadata.get("label") or category.replace("_", " ").title()
            lines.append(f"- **{label}:** {document.text}")
        return "\n".join(lines)

    def search(self, query: str, *, top_k: int = 5) -> List[InsightDocument]:
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

    # Internals --------------------------------------------------------------
    def _build_documents(self, snapshot: Dict[str, Any]) -> Iterable[InsightDocument]:
        yield from self._registration_documents(snapshot.get("registrations", {}))
        yield from self._collection_documents("schools", snapshot.get("schools", {}))
        yield from self._collection_documents("centers", snapshot.get("centers", {}))
        scope = snapshot.get("scope")
        if scope:
            label = scope.get("type", "scope").title()
            yield InsightDocument(
                text=self._format_scope(scope),
                metadata={"category": "scope", "label": label},
            )

    def _registration_documents(self, registrations: Dict[str, Any]) -> Iterable[InsightDocument]:
        total = registrations.get("total")
        if total is not None:
            yield InsightDocument(
                text=f"There are {total} active registrations in scope.",
                metadata={"category": "registrations", "label": "Registrations"},
            )

        for group_key in ("by_round", "by_partner", "by_governorate", "by_gender", "by_nationality", "by_package_type"):
            for item in registrations.get(group_key, []):
                text = self._format_group_item(group_key, item, noun="registrations")
                if text:
                    yield InsightDocument(text=text, metadata={"category": group_key, "label": group_key})

        for point in registrations.get("monthly_trend", []):
            month = point.get("month")
            count = point.get("registrations")
            if month and count is not None:
                yield InsightDocument(
                    text=f"{count} registrations were recorded during {month}.",
                    metadata={"category": "monthly_trend", "label": "Monthly trend"},
                )

        for record in registrations.get("records", [])[:10]:
            pieces = [
                record.get("child_name"),
                record.get("partner"),
                record.get("center"),
                record.get("round"),
            ]
            summary = ", ".join(piece for piece in pieces if piece)
            if not summary:
                summary = f"Registration #{record.get('id')}"
            yield InsightDocument(
                text=f"Recent registration: {summary}.",
                metadata={"category": "records", "label": "Recent registrations"},
            )

    def _collection_documents(self, name: str, section: Dict[str, Any]) -> Iterable[InsightDocument]:
        total = section.get("total")
        if total is not None:
            yield InsightDocument(
                text=f"There are {total} {name} in scope.",
                metadata={"category": name, "label": name.title()},
            )
        for key in ("by_governorate", "by_partner", "by_type"):
            for item in section.get(key, []):
                text = self._format_group_item(key, item, noun=name)
                if text:
                    yield InsightDocument(text=text, metadata={"category": f"{name}_{key}", "label": name.title()})

    def _format_group_item(self, key: str, item: Dict[str, Any], *, noun: str) -> Optional[str]:
        if not item:
            return None
        count = item.get("count")
        if count is None:
            return None
        descriptors: List[str] = []
        for field, value in item.items():
            if field == "count" or value in (None, "Unknown"):
                continue
            descriptors.append(str(value))
        if not descriptors:
            descriptors.append(key.replace("_", " "))
        label = ", ".join(descriptors)
        noun_label = noun.replace("_", " ")
        return f"{count} {noun_label} associated with {label}."

    @staticmethod
    def _format_scope(scope: Dict[str, Any]) -> str:
        descriptors = []
        if scope.get("type") == "global":
            return "Chatbot is operating with global visibility."
        username = scope.get("username")
        if username:
            descriptors.append(f"user {username}")
        if scope.get("partner"):
            partner = scope["partner"].get("name")
            if partner:
                descriptors.append(f"partner {partner}")
        if scope.get("center"):
            center = scope["center"].get("name")
            if center:
                descriptors.append(f"center {center}")
        for key in ("locations", "regions"):
            entries = scope.get(key) or []
            if entries:
                names = ", ".join(entry.get("name", "") for entry in entries if entry.get("name"))
                if names:
                    descriptors.append(f"{key.replace('_', ' ')} {names}")
        description = ", ".join(descriptors) if descriptors else "restricted scope"
        return f"Chatbot scope limited to {description}."

    def _build_faiss_index(self):
        if faiss is None or np is None:
            return None
        if not self._vectors:
            return None
        matrix = self._as_matrix(self._vectors)
        index = faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        return index

    def _fallback_rank(self, vector: Sequence[float], k: int) -> List[InsightDocument]:
        scored = []
        for document, doc_vector in zip(self.documents, self._vectors):
            score = self._cosine_similarity(vector, doc_vector)
            scored.append((score, document))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [document for _, document in scored[:k]]

    @staticmethod
    def _cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
        numerator = sum(x * y for x, y in zip(a, b))
        denom_a = math.sqrt(sum(x * x for x in a))
        denom_b = math.sqrt(sum(y * y for y in b))
        if denom_a == 0.0 or denom_b == 0.0:
            return 0.0
        return numerator / (denom_a * denom_b)

    @staticmethod
    def _as_matrix(vectors: Sequence[Sequence[float]]):
        if np is None:
            raise RuntimeError("NumPy is required to build a FAISS index")
        return np.array(vectors, dtype="float32")

