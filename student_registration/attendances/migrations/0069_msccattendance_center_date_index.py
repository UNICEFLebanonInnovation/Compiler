"""Index on Makani attendance by centre and date, for the wellbeing flags.

Built with CREATE INDEX CONCURRENTLY: the table stays writable while the index is built (it can
take several minutes on a large table). Concurrent builds cannot run inside a transaction, hence
``atomic = False``.
"""

from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations, models


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("attendances", "0068_alter_msccattendance_education_program"),
    ]

    operations = [
        AddIndexConcurrently(
            model_name="msccattendance",
            index=models.Index(fields=["center", "attendance_date"], name="mscc_attendance_center_date"),
        ),
    ]
