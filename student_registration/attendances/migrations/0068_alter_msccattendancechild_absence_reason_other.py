from django.db import migrations, models


VIEW_NAME = 'vw_mscc_attendance_data'
FIELD_NAME = 'absence_reason_other'


def _field(max_length):
    field = models.CharField(
        blank=True,
        max_length=max_length,
        null=True,
        verbose_name='specify',
    )
    field.set_attributes_from_name(FIELD_NAME)
    return field


def _get_view_definition(cursor):
    cursor.execute("SELECT to_regclass(%s)", [VIEW_NAME])
    view_regclass = cursor.fetchone()[0]
    if not view_regclass:
        return None

    cursor.execute("SELECT pg_get_viewdef(%s::regclass, true)", [VIEW_NAME])
    return cursor.fetchone()[0]


def _alter_field_preserving_view(apps, schema_editor, old_length, new_length):
    MSCCAttendanceChild = apps.get_model('attendances', 'MSCCAttendanceChild')
    old_field = _field(old_length)
    new_field = _field(new_length)

    if schema_editor.connection.vendor != 'postgresql':
        schema_editor.alter_field(MSCCAttendanceChild, old_field, new_field)
        return

    with schema_editor.connection.cursor() as cursor:
        view_definition = _get_view_definition(cursor)
        if view_definition:
            cursor.execute('DROP VIEW {}'.format(schema_editor.quote_name(VIEW_NAME)))

        schema_editor.alter_field(MSCCAttendanceChild, old_field, new_field)

        if view_definition:
            cursor.execute(
                'CREATE VIEW {} AS {}'.format(
                    schema_editor.quote_name(VIEW_NAME),
                    view_definition,
                )
            )


def forwards(apps, schema_editor):
    _alter_field_preserving_view(apps, schema_editor, old_length=500, new_length=1000)


def backwards(apps, schema_editor):
    _alter_field_preserving_view(apps, schema_editor, old_length=1000, new_length=500)


class Migration(migrations.Migration):

    dependencies = [
        ('attendances', '0067_clmattendance_section'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(forwards, backwards),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='msccattendancechild',
                    name='absence_reason_other',
                    field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='specify'),
                ),
            ],
        ),
    ]
