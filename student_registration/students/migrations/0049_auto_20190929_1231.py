# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-09-29 09:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import student_registration.students.models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0048_auto_20190928_0838'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='recordnumber',
            field=models.CharField(blank=True, max_length=45, null=True),
        ),
        # migrations.AlterField(
        #     model_name='student',
        #     name='birthdoc_image',
        #     field=models.ImageField(blank=True, help_text='UNHCR File \u0635\u0648\u0631\u0629 \u0639\u0646 \u0634\u0647\u0627\u062f\u0629 \u0627\u0644\u0648\u0644\u0627\u062f\u0629 \u0627\u0644\u0645\u0633\u062c\u0644\u0629 \u0641\u064a \u062f\u0627\u0626\u0631\u0629 \u0627\u0644\u0646\u0641\u0648\u0633', null=True, upload_to='profiles/birthdoc', validators=[student_registration.students.models.validate_file_size]),
        # ),
        migrations.AlterField(
            model_name='student',
            name='financialsupport',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='financialsupport', to='students.FinancialSupport', verbose_name='\u0628\u0631\u0627\u0645\u062c \u0627\u0644\u062f\u0639\u0645 \u0627\u0644\u0645\u0627\u062f\u064a'),
        ),
        # migrations.AlterField(
        #     model_name='student',
        #     name='unhcr_image',
        #     field=models.ImageField(blank=True, help_text='\u0635\u0648\u0631\u0629 \u0639\u0646 \u0628\u0637\u0627\u0642\u0629 \u0627\u0644\u0639\u0627\u0626\u0644\u0629 \u0644\u062f\u0649 \u0627\u0644\u0645\u0641\u0648\u0636\u064a\u0629 \u0627\u0644\u0633\u0627\u0645\u064a\u0629 \u0644\u0644\u0627\u0645\u0645 \u0627\u0644\u0645\u062a\u062d\u062f\u0629 \u0644\u0634\u0624\u0648\u0646 \u0627\u0644\u0644\u0627\u062c\u0626\u064a\u0646', null=True, upload_to='profiles/unhcr', validators=[student_registration.students.models.validate_file_size]),
        # ),
    ]
