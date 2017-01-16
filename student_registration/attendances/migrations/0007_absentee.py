# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-01-16 10:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0008_auto_20161207_1610'),
        ('students', '0020_auto_20161230_2049'),
        ('attendances', '0006_auto_20170113_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='Absentee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('last_attendance_date', models.DateField(blank=True, null=True)),
                ('absent_days', models.IntegerField(blank=True, null=True)),
                ('reattend_date', models.DateField(blank=True, null=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.School')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='absents', to='students.Student')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
