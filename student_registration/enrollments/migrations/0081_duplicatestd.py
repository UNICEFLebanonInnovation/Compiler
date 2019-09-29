# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-08-12 09:55
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('enrollments', '0080_auto_20190521_1343'),
    ]

    operations = [
        migrations.CreateModel(
            name='DuplicateStd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sysdate', models.DateTimeField(default=datetime.date.today)),
                ('is_solved', models.BooleanField(default=False)),
                ('remark', models.CharField(blank=True, max_length=500)),
                ('school_type', models.CharField(max_length=20)),
                ('enrollment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollment_id', to='enrollments.Enrollment')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='added_by', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]