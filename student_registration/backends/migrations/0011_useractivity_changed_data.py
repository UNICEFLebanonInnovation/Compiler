# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backends', '0010_useractivity'),
    ]

    operations = [
        migrations.AddField(
            model_name='useractivity',
            name='changed_data',
            field=models.TextField(blank=True, null=True),
        ),
    ]
