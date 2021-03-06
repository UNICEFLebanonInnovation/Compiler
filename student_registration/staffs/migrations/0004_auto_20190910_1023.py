# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-09-10 07:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staffs', '0003_remove_staffs_have_children'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Banks',
            new_name='Bank',
        ),
        migrations.AddField(
            model_name='staffs',
            name='bank',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staffs.Bank', verbose_name='Bank'),
        ),
        migrations.AddField(
            model_name='staffs',
            name='branch',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Branch'),
        ),
        migrations.AddField(
            model_name='staffs',
            name='certificate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staffs.Certificate', verbose_name='Certificate'),
        ),
        migrations.AddField(
            model_name='staffs',
            name='iban',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='IBAN'),
        ),
        migrations.AddField(
            model_name='staffs',
            name='type_of_employment',
            field=models.CharField(blank=True, choices=[('Cadre', 'Cadre'), ('Contractual', 'Contractual'), ('Supporter', 'Supporter')], max_length=80, null=True, verbose_name='Type on Employment'),
        ),
        migrations.AddField(
            model_name='staffs',
            name='university',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staffs.University', verbose_name='University Name'),
        ),
        migrations.AlterField(
            model_name='staffs',
            name='nationality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='students.Nationality', verbose_name=' \u0627\u0644\u062c\u0646\u0633\u064a\u0629'),
        ),
    ]
