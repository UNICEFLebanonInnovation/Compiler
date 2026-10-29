"""Bound database time across a preview, including waits for database locks."""
from contextlib import contextmanager
from time import monotonic

from django.db import connection, OperationalError, transaction


class PreviewTimeout(Exception):
    pass


@contextmanager
def preview_budget(seconds=5):
    deadline = monotonic() + seconds
    with transaction.atomic():
        original = 0
        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute("SELECT setting::int FROM pg_settings WHERE name='statement_timeout'")
                original = cursor.fetchone()[0]

        def bounded_execute(execute, sql, params, many, context):
            remaining = int((deadline - monotonic()) * 1000)
            if remaining <= 0:
                raise PreviewTimeout
            if connection.vendor == 'postgresql':
                limit = min(remaining, original) if original else remaining
                # Use the driver's cursor for this control statement so the
                # execution wrapper does not call itself recursively.
                with connection.connection.cursor() as cursor:
                    cursor.execute("SELECT set_config('statement_timeout', %s, true)", [str(limit)])
            return execute(sql, params, many, context)

        try:
            with connection.execute_wrapper(bounded_execute):
                yield
        except OperationalError as error:
            cause = error.__cause__
            if getattr(cause, 'sqlstate', None) == '57014' or getattr(cause, 'pgcode', None) == '57014':
                raise PreviewTimeout from error
            raise
        else:
            # SET LOCAL also lives across a savepoint. Restore the caller's
            # timeout on success; rollback restores it after an exception.
            if connection.vendor == 'postgresql':
                with connection.cursor() as cursor:
                    cursor.execute("SELECT set_config('statement_timeout', %s, true)", [str(original)])
