# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-13 13:35
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0007_auto_20171009_1542'),
    ]

    operations = [
        migrations.CreateModel(
            name='SelfPerceptionGrades',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assessment_type', models.CharField(blank=True, max_length=50, null=True)),
                ('assessment_date', models.DateTimeField(blank=True, null=True)),
                ('answers', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, null=True)),
                ('enrollment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='clm.BLN')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
    ]
