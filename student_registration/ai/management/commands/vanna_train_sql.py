"""Management command to train the Vanna agent with question/SQL pairs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError

from student_registration.ai.services import get_vanna_service


class Command(BaseCommand):
    """Train the configured Vanna client with question/SQL examples."""

    help = (
        "Train the configured Vanna client with question/SQL pairs. Either provide "
        "a CSV/JSON file containing `question` and `sql` keys or pass them "
        "explicitly via --question/--sql."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "source",
            nargs="?",
            help="Optional path to a CSV or JSON file containing training data.",
        )
        parser.add_argument(
            "--format",
            choices=("csv", "json"),
            help="Explicitly specify the file format when auto-detection is insufficient.",
        )
        parser.add_argument("--question", help="Single training question to register.")
        parser.add_argument("--sql", help="SQL statement associated with the question.")

    def _load_from_json(self, path: Path) -> List[Dict[str, str]]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"Failed to parse JSON data from {path}: {exc}") from exc

        if not isinstance(payload, list):
            raise CommandError("JSON payload must be a list of objects.")

        entries: List[Dict[str, str]] = []
        for item in payload:
            if not isinstance(item, dict):
                raise CommandError("Each JSON entry must be an object with question/sql keys.")
            question = item.get("question")
            sql = item.get("sql")
            if not question or not sql:
                raise CommandError("Each JSON entry must contain both 'question' and 'sql'.")
            entries.append({"question": str(question), "sql": str(sql)})
        return entries

    def _load_from_csv(self, path: Path) -> List[Dict[str, str]]:
        entries: List[Dict[str, str]] = []
        with path.open(encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if "question" not in reader.fieldnames or "sql" not in reader.fieldnames:
                raise CommandError(
                    "CSV file must contain 'question' and 'sql' columns."
                )
            for row in reader:
                question = row.get("question")
                sql = row.get("sql")
                if not question or not sql:
                    raise CommandError(
                        "Each CSV row must contain non-empty 'question' and 'sql' values."
                    )
                entries.append({"question": question, "sql": sql})
        return entries

    def _entries_from_options(self, options: Dict[str, str]) -> Iterable[Dict[str, str]]:
        question = options.get("question")
        sql = options.get("sql")
        if question and sql:
            yield {"question": question, "sql": sql}

    def handle(self, *args, **options) -> None:
        entries: List[Dict[str, str]] = []

        source = options.get("source")
        if source:
            path = Path(source)
            if not path.exists():
                raise CommandError(f"Training data file not found: {path}")

            file_format = options.get("format") or path.suffix.lstrip(".").lower()
            if file_format == "json":
                entries.extend(self._load_from_json(path))
            elif file_format == "csv":
                entries.extend(self._load_from_csv(path))
            else:
                raise CommandError(
                    "Unable to determine file format. Specify --format=csv or --format=json."
                )

        entries.extend(self._entries_from_options(options))

        if not entries:
            raise CommandError(
                "No training data provided. Supply a source file or the --question/--sql options."
            )

        try:
            service = get_vanna_service()
        except ImproperlyConfigured as exc:
            raise CommandError(str(exc)) from exc

        for index, entry in enumerate(entries, start=1):
            question = entry["question"].strip()
            sql = entry["sql"].strip()
            if not question or not sql:
                raise CommandError("Empty question or SQL encountered in the training data.")

            self.stdout.write(f"[{index}/{len(entries)}] Training: {question!r}")
            try:
                service.train_sql(question=question, sql=sql)
            except ImproperlyConfigured as exc:
                raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS("Training data successfully submitted."))
