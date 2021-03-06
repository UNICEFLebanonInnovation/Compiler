# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-06-21 13:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0014_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='ALPAssignmentMatrix',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('range_start', models.IntegerField(blank=True, null=True)),
                ('range_end', models.IntegerField(blank=True, null=True)),
                ('fail_refer_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fail_refer_to', to='schools.EducationLevel')),
                ('level', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.EducationLevel')),
                ('success_refer_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='success_refer_to', to='schools.EducationLevel')),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'ALP Pre-test Refer Matrix',
            },
        ),
        migrations.AlterModelOptions(
            name='alprefermatrix',
            options={'ordering': ['id'], 'verbose_name': 'ALP Post-test Refer Matrix'},
        ),
    ]
