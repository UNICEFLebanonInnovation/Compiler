# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youth', '0037_registration_education_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='dropout_date',
            field=models.DateField(blank=True, null=True, verbose_name='Please Specify dropout date from school'),
        ),
    ]
