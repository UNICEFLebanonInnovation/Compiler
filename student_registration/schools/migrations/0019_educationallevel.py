# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-20 18:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0018_auto_20170809_1524'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationalLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, unique=True)),
                ('note', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
