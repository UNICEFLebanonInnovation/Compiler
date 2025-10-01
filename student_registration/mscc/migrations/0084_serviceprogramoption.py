from django.db import migrations, models


SERVICE_PROGRAM_MAPPING = [
    ('BLN', [
        'BLN Level 1',
        'BLN Level 2',
        'BLN Level 3',
    ]),
    ('BLN Catch-up', [
        'BLN Catch-up',
    ]),
    ('CB-ECE', [
        'CBECE Level 1',
        'CBECE Level 2',
        'CBECE Level 3',
    ]),
    ('CB-ECE Catch-up', [
        'CBECE Catch-up',
    ]),
    ('ABLN', [
        'ABLN Level 1',
        'ABLN Level 2',
    ]),
    ('ABLN Catch-up', [
        'ABLN Catch-up',
    ]),
    ('RS', [
        'RS Grade 1',
        'RS Grade 2',
        'RS Grade 3',
        'RS Grade 4',
        'RS Grade 5',
        'RS Grade 6',
        'RS Grade 7',
        'RS Grade 8',
        'RS Grade 9',
    ]),
    ('YBLN', [
        'YBLN Level 1',
        'YBLN Level 2',
    ]),
    ('YBLN Catch-up', [
        'YBLN Catch-up',
    ]),
    ('YFS', [
        'YFS Level 1',
        'YFS Level 2',
    ]),
    ('ECD', [
        'ECD',
    ]),
    ('RS-YFS', [
        'YFS Level 1 - RS Grade 9',
        'YFS Level 2 - RS Grade 9',
    ]),
]


def populate_service_program_options(apps, schema_editor):
    ServiceProgramOption = apps.get_model('mscc', 'ServiceProgramOption')

    objects = [
        ServiceProgramOption(service_name=service, program_code=program)
        for service, programs in SERVICE_PROGRAM_MAPPING
        for program in programs
    ]

    ServiceProgramOption.objects.bulk_create(objects, ignore_conflicts=True)


def remove_service_program_options(apps, schema_editor):
    ServiceProgramOption = apps.get_model('mscc', 'ServiceProgramOption')

    for service, programs in SERVICE_PROGRAM_MAPPING:
        ServiceProgramOption.objects.filter(
            service_name=service,
            program_code__in=programs,
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0083_round_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceProgramOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(max_length=100)),
                ('program_code', models.CharField(max_length=100)),
            ],
            options={
                'ordering': ['service_name', 'program_code'],
                'verbose_name': 'Service Program Option',
                'verbose_name_plural': 'Service Program Options',
                'unique_together': {('service_name', 'program_code')},
            },
        ),
        migrations.RunPython(populate_service_program_options, remove_service_program_options),
    ]
