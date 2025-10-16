"""Utilities that wire the project to the Vanna integration layer."""

from __future__ import annotations

import importlib
import json
from typing import Any, Callable, Dict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _load_class(import_path: str) -> type:
    """Return a class from a dotted ``module.ClassName`` path."""

    if not import_path or "." not in import_path:
        raise ImproperlyConfigured(
            "VANNA.CLIENT_CLASS must be a dotted path to the Vanna client implementation."
        )
    module_path, class_name = import_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    try:
        return getattr(module, class_name)
    except AttributeError as exc:
        raise ImproperlyConfigured(
            f"Class '{class_name}' could not be located in module '{module_path}'."
        ) from exc


def _clean_kwargs(raw_kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Remove empty values from keyword arguments."""

    return {key: value for key, value in raw_kwargs.items() if value not in (None, "")}


def _connection_kwargs(raw_value: Any) -> Dict[str, Any]:
    """Parse connection kwargs from settings."""

    if isinstance(raw_value, dict):
        return raw_value
    if raw_value in (None, ""):
        return {}
    if isinstance(raw_value, str):
        try:
            return json.loads(raw_value)
        except ValueError as exc:
            raise ImproperlyConfigured(
                "VANNA.CONNECTION_KWARGS must be valid JSON when provided as a string."
            ) from exc
    raise ImproperlyConfigured(
        "VANNA.CONNECTION_KWARGS must be provided as a dict or JSON encoded string."
    )


class VannaService:
    """High level helper responsible for interacting with Vanna."""

    def __init__(self) -> None:
        configuration = getattr(settings, "VANNA", {})
        if not configuration.get("ENABLED"):
            raise ImproperlyConfigured("Vanna integration is disabled. Enable it via VANNA.ENABLED.")

        client_class_path = configuration.get("CLIENT_CLASS")
        client_class = _load_class(client_class_path)

        client_kwargs = _clean_kwargs(configuration.get("CLIENT_KWARGS", {}))
        self._client = client_class(**client_kwargs)

        connection_method = configuration.get("CONNECTION_METHOD")
        if connection_method:
            if not hasattr(self._client, connection_method):
                raise ImproperlyConfigured(
                    f"Configured Vanna client does not define '{connection_method}'."
                )
            kwargs = _connection_kwargs(configuration.get("CONNECTION_KWARGS"))
            getattr(self._client, connection_method)(**kwargs)

        self._ask_method = configuration.get("ASK_METHOD", "ask")
        self._generate_sql_method = configuration.get("GENERATE_SQL_METHOD", "generate_sql")
        self._run_sql_method = configuration.get("RUN_SQL_METHOD", "run_sql")
        self._train_sql_method = configuration.get("TRAIN_SQL_METHOD", "train_sql")
        self._train_documentation_method = configuration.get(
            "TRAIN_DOCUMENTATION_METHOD", "train_documentation"
        )
        self._train_ddl_method = configuration.get("TRAIN_DDL_METHOD", "train_ddl")

    @property
    def client(self) -> Any:
        """Expose the underlying Vanna client for advanced usages."""

        return self._client

    def _call_if_available(self, method_name: str, *args: Any, **kwargs: Any) -> Any:
        """Invoke a method when present on the Vanna client."""

        if not method_name:
            return None
        if not hasattr(self._client, method_name):
            return None
        method = getattr(self._client, method_name)
        return method(*args, **kwargs)

    def _require_method(self, method_name: str) -> Callable[..., Any]:
        """Return a callable method on the client or raise configuration errors."""

        if not method_name:
            raise ImproperlyConfigured(
                "No method configured for the requested Vanna interaction."
            )
        if not hasattr(self._client, method_name):
            raise ImproperlyConfigured(
                f"Configured Vanna client does not define '{method_name}'."
            )
        return getattr(self._client, method_name)

    @staticmethod
    def _serialise_result(result: Any) -> Any:
        """Attempt to serialise a SQL execution result."""

        if hasattr(result, "to_dict"):
            try:
                return result.to_dict(orient="records")  # type: ignore[call-arg]
            except TypeError:
                return result.to_dict()  # type: ignore[call-arg]
        if isinstance(result, (list, tuple)):
            return list(result)
        if isinstance(result, dict):
            return result
        return result

    def ask(self, question: str, run_sql: bool = False) -> Dict[str, Any]:
        """Submit a natural language question to Vanna and return the answer payload."""

        payload: Dict[str, Any] = {"question": question}

        answer = self._call_if_available(self._ask_method, question)
        if answer is not None:
            payload["answer"] = self._serialise_result(answer)

        sql = self._call_if_available(self._generate_sql_method, question)
        if sql is not None:
            payload["sql"] = sql
            if run_sql:
                result = self._call_if_available(self._run_sql_method, sql)
                if result is not None:
                    payload["results"] = self._serialise_result(result)

        if len(payload) == 1:
            raise ImproperlyConfigured(
                "Vanna client does not implement any supported interaction methods."
            )

        return payload

    def train_sql(self, *, question: str, sql: str) -> Any:
        """Train the Vanna client with a question/SQL pair."""

        method = self._require_method(self._train_sql_method)
        return method(question=question, sql=sql)

    def train_documentation(self, *, title: str, content: str) -> Any:
        """Train the Vanna client with supplemental documentation."""

        method = self._require_method(self._train_documentation_method)
        return method(title=title, text=content)

    def train_ddl(self, ddl: str) -> Any:
        """Train the Vanna client with database DDL definitions."""

        method = self._require_method(self._train_ddl_method)
        return method(ddl=ddl)


_vanna_service: VannaService | None = None


def get_vanna_service() -> VannaService:
    """Return a cached instance of :class:`VannaService`."""

    global _vanna_service
    if _vanna_service is None:
        _vanna_service = VannaService()
    return _vanna_service
