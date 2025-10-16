"""Management command to train the Vanna agent with documentation snippets."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError

from student_registration.ai.services import get_vanna_service


class Command(BaseCommand):
    """Train the configured Vanna client with documentation content."""

    help = (
        "Submit documentation snippets to the configured Vanna client. Provide one or "
        "more files as positional arguments. Optionally use --title/--content for a "
        "single ad-hoc snippet."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "documents",
            nargs="*",
            help="One or more text/Markdown files containing documentation to ingest.",
        )
        parser.add_argument("--title", help="Title to associate with the documentation snippet.")
        parser.add_argument(
            "--content",
            help="Documentation content provided directly on the command line.",
        )

    def _iter_file_documents(self, paths: Iterable[str]) -> Iterable[Tuple[str, str]]:
        for raw_path in paths:
            path = Path(raw_path)
            if not path.exists():
                raise CommandError(f"Documentation file not found: {path}")
            yield (path.stem, path.read_text(encoding="utf-8"))

    def handle(self, *args, **options) -> None:
        documents = list(self._iter_file_documents(options.get("documents", [])))

        inline_content = options.get("content")
        inline_title = options.get("title")
        if inline_content:
            if not inline_title:
                raise CommandError("--title is required when providing inline --content.")
            documents.append((inline_title, inline_content))

        if not documents:
            raise CommandError(
                "No documentation supplied. Provide files or the --title/--content options."
            )

        try:
            service = get_vanna_service()
        except ImproperlyConfigured as exc:
            raise CommandError(str(exc)) from exc

        for index, (title, content) in enumerate(documents, start=1):
            title = title.strip()
            content = content.strip()
            if not title or not content:
                raise CommandError("Documentation entries must include both title and content.")

            self.stdout.write(f"[{index}/{len(documents)}] Training documentation: {title!r}")
            try:
                service.train_documentation(title=title, content=content)
            except ImproperlyConfigured as exc:
                raise CommandError(str(exc)) from exc

        self.stdout.write(self.style.SUCCESS("Documentation successfully submitted."))
