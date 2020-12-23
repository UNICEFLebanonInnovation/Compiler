# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-12-23 12:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0183_auto_20201222_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='rs',
            name='grade_registration',
            field=models.CharField(blank=True, choices=[('', '----------'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9')], max_length=100, null=True, verbose_name='Grade of registeration'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='grade_level',
            field=models.CharField(blank=True, choices=[('grade1', 'Grade 1'), ('grade2', 'Grade 2'), ('grade3', 'Grade 3'), ('grade4', 'Grade 4'), ('grade5', 'Grade 5'), ('grade6', 'Grade 6'), ('grade7', 'Grade 7'), ('grade8', 'Grade 8'), ('grade9', 'Grade 9')], max_length=50, null=True, verbose_name='\u0645\u0627 \u0647\u0648 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u062a\u0639\u0644\u064a\u0645\u064a \u0644\u0644\u0637\u0641\u0644 \u0639\u0646\u062f \u0627\u0644\u062a\u0633\u062c\u064a\u0644 \u0644\u0623\u0648\u0644 \u0645\u0631\u0629 \u0641\u064a \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0627\u0644\u0631\u0633\u0645\u064a \u0641\u064a \u0644\u0628\u0646\u0627\u0646'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='registered_in_school',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schools.School', verbose_name='School of Enrollment'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='source_join_fe',
            field=models.CharField(blank=True, choices=[('ALP', 'ALP'), ('Prep-ECE', 'Prep - ECE'), ('ABLN', 'ABLN'), ('CBECE', 'CBECE'), ('BLN', 'BLN'), ('YBLN', 'YBLN'), ('FE_outside_lebanon', '\u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0627\u0644\u0631\u0633\u0645\u064a \u062e\u0627\u0631\u062c \u0644\u0628\u0646\u0627\u0646')], max_length=50, null=True, verbose_name=' \u0645\u0635\u062f\u0631 \u0625\u062d\u0627\u0644\u0629 \u0627\u0644\u0637\u0641\u0644 \u0639\u0646\u062f \u0627\u0644\u062a\u0633\u062c\u064a\u0644 \u0644\u0623\u0648\u0644 \u0645\u0631\u0629 \u0641\u064a \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0627\u0644\u0631\u0633\u0645\u064a'),
        ),
    ]
