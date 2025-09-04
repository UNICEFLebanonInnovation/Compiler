# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import JSONField


class Migration(migrations.Migration):

    dependencies = [
        ('backends', '0014_auto_20250702_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='exporthistory',
            name='fields',
            field=JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='exporthistory',
            name='file_format',
            field=models.CharField(default='csv', max_length=10),
        ),
        migrations.AddField(
            model_name='exporthistory',
            name='file_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='exporthistory',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('done', 'Done'), ('failed', 'Failed')], default='pending', max_length=10),
        ),
    ]
