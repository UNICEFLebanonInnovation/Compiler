"""Management command to train the Vanna agent with database DDL."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError

from student_registration.ai.services import get_vanna_service


class Command(BaseCommand):
    """Submit database DDL statements to the configured Vanna client."""

    help = (
        "Send database DDL statements to the Vanna client. Provide one or more files "
        "containing SQL DDL or use the --ddl option for inline statements."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "ddl_files",
            nargs="*",
            help="Files containing SQL DDL statements to register with Vanna.",
        )
        parser.add_argument("--ddl", help="Inline SQL DDL provided directly on the command line.")

    def _iter_file_contents(self, paths: Iterable[str]) -> Iterable[str]:
        for raw_path in paths:
            path = Path(raw_path)
            if not path.exists():
                raise CommandError(f"DDL file not found: {path}")
            yield path.read_text(encoding="utf-8")

    def handle(self, *args, **options) -> None:
        ddl_statements = list(self._iter_file_contents(options.get("ddl_files", [])))

        inline_ddl = options.get("ddl")
        if inline_ddl:
            ddl_statements.append(inline_ddl)

        if not ddl_statements:
            raise CommandError("Provide at least one DDL file or use the --ddl option.")

        try:
            service = get_vanna_service()
        except ImproperlyConfigured as exc:
            raise CommandError(str(exc)) from exc

        for index, ddl in enumerate(ddl_statements, start=1):
            ddl = ddl.strip()
            if not ddl:
                raise CommandError("Encountered an empty DDL statement in the payload.")

            self.stdout.write(f"[{index}/{len(ddl_statements)}] Training DDL chunk")
            try:
                service.train_ddl(ddl)
            except ImproperlyConfigured as exc:
                raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS("DDL successfully submitted."))
