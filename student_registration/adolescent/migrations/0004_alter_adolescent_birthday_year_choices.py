# -*- coding: utf-8 -*-
# Generated manually to keep model-level birthday year validation in sync with youth forms.
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adolescent', '0003_auto_20250217_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adolescent',
            name='birthday_year',
            field=models.CharField(
                blank=True,
                choices=[(str(x), x) for x in range(1980, 2050)],
                default=0,
                max_length=4,
                null=True,
                verbose_name='Birthday year',
            ),
        ),
    ]
