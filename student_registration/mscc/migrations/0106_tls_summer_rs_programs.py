from django.db import migrations


def enable_tls_summer_rs(apps, schema_editor):
    ServiceProgramOption = apps.get_model('mscc', 'ServiceProgramOption')
    options = ServiceProgramOption.objects.using(schema_editor.connection.alias)
    for grade in range(1, 10):
        options.update_or_create(
            service_name='RS',
            program_code='Summer RS Grade {}'.format(grade),
            defaults={'is_tls': 'Yes', 'is_education': 'Yes'},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0105_registration_profile_picture'),
    ]

    operations = [
        migrations.RunPython(enable_tls_summer_rs, migrations.RunPython.noop),
    ]
