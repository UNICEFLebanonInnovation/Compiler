# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-08-18 17:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0042_auto_20171201_1630'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='std_image',
            field=models.ImageField(blank=True, help_text='Profile Picture', null=True, upload_to='profiles', verbose_name='Profile Picture'),
        ),
    ]
