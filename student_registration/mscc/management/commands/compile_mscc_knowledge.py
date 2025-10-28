"""Management command to compile MSCC knowledge snapshots."""

from __future__ import annotations

import json
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from student_registration.mscc.knowledge import MSCCKnowledgeCompiler


class Command(BaseCommand):
    """Compile MSCC knowledge snapshots for the AI agent."""

    help = (
        "Compile the MSCC knowledge snapshot for the AI agent. By default the snapshot "
        "is persisted and summary statistics are printed."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of registrations compiled into the snapshot.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Compile the snapshot without persisting it to the database.',
        )
        parser.add_argument(
            '--include-documents',
            action='store_true',
            help='When used with --dry-run, include the compiled documents in the output.',
        )

    def handle(self, *args: Any, **options: Any) -> None:
        limit = options.get('limit')
        dry_run: bool = options.get('dry_run', False)
        include_documents: bool = options.get('include_documents', False)

        if include_documents and not dry_run:
            raise CommandError('--include-documents can only be used together with --dry-run.')

        compiler = MSCCKnowledgeCompiler(limit=limit)

        if dry_run:
            compilation = compiler.compile()
            self.stdout.write(
                self.style.SUCCESS(
                    'Compiled MSCC knowledge: '
                    f"generated_at={compilation.generated_at.isoformat()} "
                    f"children={len(compilation.children)} documents={len(compilation.documents)}"
                )
            )
            self.stdout.write(compilation.summary or 'No summary generated.')

            metadata = {
                'generated_at': compilation.generated_at.isoformat(),
                'children_count': len(compilation.children),
                'document_count': len(compilation.documents),
                'vulnerability_overview': compilation.vulnerability_overview,
            }
            self.stdout.write(json.dumps(metadata, indent=2, default=str))

            if include_documents:
                self.stdout.write(
                    json.dumps(compilation.documents, indent=2, default=str)
                )
            return

        snapshot = compiler.create_snapshot()
        payload = snapshot.as_openai_payload()

        self.stdout.write(
            self.style.SUCCESS(
                'MSCC knowledge snapshot created: '
                f"id={snapshot.pk} generated_for={snapshot.generated_for.isoformat()}"
            )
        )

        summary = {
            'generated_for': snapshot.generated_for.isoformat(),
            'children_count': len(payload.get('children') or []),
            'document_count': snapshot.document_count,
            'metadata_keys': sorted((payload.get('metadata') or {}).keys()),
        }
        self.stdout.write(json.dumps(summary, indent=2, default=str))

