# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0080_auto_20250703_2003'),
    ]

    operations = [
        migrations.CreateModel(
            name='MSCCExportRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('fields', models.JSONField(blank=True, null=True)),
                ('file_format', models.CharField(default='csv', max_length=10)),
                ('file_url', models.URLField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('done', 'Done'), ('failed', 'Failed')], default='pending', max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mscc_export_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'MSCC Export Request',
                'verbose_name_plural': 'MSCC Export Requests',
                'ordering': ['-created'],
            },
        ),
    ]
