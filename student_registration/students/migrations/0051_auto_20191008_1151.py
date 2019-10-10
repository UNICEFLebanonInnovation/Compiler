# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-10-08 08:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import student_registration.students.models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0050_auto_20190929_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='Financialsupport_number',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='\u0631\u0642\u0645 \u0627\u0644\u062f\u0639\u0645 \u0627\u0644\u0645\u0627\u062f\u064a'),
        ),
        migrations.AlterField(
            model_name='student',
            name='birthdoc_image',
            field=models.ImageField(blank=True, help_text='\u0635\u0648\u0631\u0629 \u0627\u0644\u0647\u0648\u064a\u0629/\u0627\u062e\u0631\u0627\u062c \u0642\u064a\u062f/\u0625\u0641\u0627\u062f\u0629 \u0645\u062e\u062a\u0627\u0631', null=True, upload_to='profiles/birthdoc', validators=[student_registration.students.models.validate_file_size]),
        ),
        migrations.AlterField(
            model_name='student',
            name='financialsupport',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='financialsupport', to='students.FinancialSupport', verbose_name='Financial Support Program'),
        ),
        migrations.AlterField(
            model_name='student',
            name='recordnumber',
            field=models.CharField(blank=True, max_length=45, null=True, verbose_name='\u0631\u0642\u0645 \u062a\u0633\u0644\u0633\u0644\u064a \u062e\u0627\u0635 \u0628\u0627\u0644\u062c\u0645\u0639\u064a\u0629'),
        ),
        migrations.AlterField(
            model_name='student',
            name='specialneeds',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='specialneeds', to='students.SpecialNeeds', verbose_name='\u0627\u0644\u0627\u062d\u062a\u064a\u0627\u062c\u0627\u062a \u0627\u0644\u062e\u0627\u0635\u0629'),
        ),
        migrations.AlterField(
            model_name='student',
            name='specialneedsdt',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='students.SpecialNeedsDt', verbose_name='\u062a\u0641\u0627\u0635\u064a\u0644 \u0627\u0644\u0627\u062d\u062a\u064a\u0627\u062c\u0627\u062a \u0627\u0644\u062e\u0627\u0635\u0629'),
        ),
        migrations.AlterField(
            model_name='student',
            name='std_image',
            field=models.ImageField(blank=True, help_text='\u0627\u0644\u0635\u0648\u0631\u0629 \u0627\u0644\u0634\u0645\u0633\u064a\u0629', null=True, upload_to='profiles', validators=[student_registration.students.models.validate_file_size], verbose_name='\u0627\u0644\u0635\u0648\u0631\u0629 \u0627\u0644\u0634\u0645\u0633\u064a\u0629'),
        ),
        migrations.AlterField(
            model_name='student',
            name='unhcr_family',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='\u0627\u0644\u0631\u0642\u0645 \u0627\u0644\u0639\u0627\u0626\u0644\u064a \u0628\u062d\u0633\u0628 \u0628\u0637\u0627\u0642\u0629 \u0627\u0644\u0645\u0641\u0648\u0636\u064a\u0629 \u0627\u0644\u0633\u0627\u0645\u064a\u0629 \u0644\u0644\u0623\u0645\u0645 \u0627\u0644\u0645\u062a\u062d\u062f\u0629'),
        ),
        migrations.AlterField(
            model_name='student',
            name='unhcr_image',
            field=models.ImageField(blank=True, help_text='\u0635\u0648\u0631\u0629 \u0639\u0646 \u0628\u0637\u0627\u0642\u0629 \u0627\u0644\u0639\u0627\u0626\u0644\u0629 \u0644\u062f\u0649 \u0627\u0644\u0645\u0641\u0648\u0636\u064a\u0629 \u0627\u0644\u0633\u0627\u0645\u064a\u0629 \u0644\u0644\u0623\u0645\u0645 \u0627\u0644\u0645\u062a\u062d\u062f\u0629 \u0644\u0634\u0624\u0648\u0646 \u0627\u0644\u0644\u0627\u062c\u0626\u064a\u0646 UNHCR File', null=True, upload_to='profiles/unhcr', validators=[student_registration.students.models.validate_file_size]),
        ),
        migrations.AlterField(
            model_name='student',
            name='unhcr_personal',
            field=models.CharField(blank=True, db_index=True, max_length=150, null=True, verbose_name='\u0627\u0644\u0631\u0642\u0645 \u0627\u0644\u0634\u062e\u0635\u064a \u0628\u062d\u0633\u0628 \u0628\u0637\u0627\u0642\u0629 \u0627\u0644\u0645\u0641\u0648\u0636\u064a\u0629 \u0627\u0644\u0633\u0627\u0645\u064a\u0629 \u0644\u0644\u0623\u0645\u0645 \u0627\u0644\u0645\u062a\u062d\u062f\u0629'),
        ),
    ]
