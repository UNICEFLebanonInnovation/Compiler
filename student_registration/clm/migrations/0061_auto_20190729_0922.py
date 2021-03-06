# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-07-29 06:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0060_auto_20190724_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='abln',
            name='no_child_id_confirmation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='abln',
            name='no_parent_id_confirmation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='abln',
            name='parent_case_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Case number'),
        ),
        migrations.AddField(
            model_name='abln',
            name='parent_case_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Case number confirm'),
        ),
        migrations.AddField(
            model_name='abln',
            name='parent_id_type',
            field=models.CharField(blank=True, choices=[('UNHCR Registered', 'UNHCR Registered'), ('Syrian national ID', 'Syrian national ID'), ('Lebanese national ID', 'Lebanese national ID'), ('Parent have no ID', 'Parent have no ID')], max_length=100, null=True, verbose_name='Parent ID type'),
        ),
        migrations.AddField(
            model_name='abln',
            name='parent_individual_case_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Individual Case number'),
        ),
        migrations.AddField(
            model_name='abln',
            name='parent_individual_case_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Individual Case number confirm'),
        ),
        migrations.AddField(
            model_name='abln',
            name='parent_national_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Syrian / Lebanese ID number '),
        ),
        migrations.AddField(
            model_name='abln',
            name='parent_national_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Syrian / Lebanese ID number confirm'),
        ),
        migrations.AddField(
            model_name='abln',
            name='source_of_identification',
            field=models.CharField(blank=True, choices=[('Family walked in to NGO', 'Family walked in to NGO'), ('Referral from another NGO or municipality', 'Referral from another NGO or municipality'), ('Direct outreach', 'Direct outreach'), ('List database', 'List database')], max_length=100, null=True, verbose_name='Source of identification of the child'),
        ),
        migrations.AddField(
            model_name='bln',
            name='no_child_id_confirmation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='bln',
            name='no_parent_id_confirmation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='bln',
            name='parent_case_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Case number'),
        ),
        migrations.AddField(
            model_name='bln',
            name='parent_case_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Case number confirm'),
        ),
        migrations.AddField(
            model_name='bln',
            name='parent_id_type',
            field=models.CharField(blank=True, choices=[('UNHCR Registered', 'UNHCR Registered'), ('Syrian national ID', 'Syrian national ID'), ('Lebanese national ID', 'Lebanese national ID'), ('Parent have no ID', 'Parent have no ID')], max_length=100, null=True, verbose_name='Parent ID type'),
        ),
        migrations.AddField(
            model_name='bln',
            name='parent_individual_case_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Individual Case number'),
        ),
        migrations.AddField(
            model_name='bln',
            name='parent_individual_case_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Individual Case number confirm'),
        ),
        migrations.AddField(
            model_name='bln',
            name='parent_national_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Syrian / Lebanese ID number '),
        ),
        migrations.AddField(
            model_name='bln',
            name='parent_national_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Syrian / Lebanese ID number confirm'),
        ),
        migrations.AddField(
            model_name='bln',
            name='source_of_identification',
            field=models.CharField(blank=True, choices=[('Family walked in to NGO', 'Family walked in to NGO'), ('Referral from another NGO or municipality', 'Referral from another NGO or municipality'), ('Direct outreach', 'Direct outreach'), ('List database', 'List database')], max_length=100, null=True, verbose_name='Source of identification of the child'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='no_child_id_confirmation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='cbece',
            name='no_parent_id_confirmation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='cbece',
            name='parent_case_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Case number'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='parent_case_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Case number confirm'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='parent_id_type',
            field=models.CharField(blank=True, choices=[('UNHCR Registered', 'UNHCR Registered'), ('Syrian national ID', 'Syrian national ID'), ('Lebanese national ID', 'Lebanese national ID'), ('Parent have no ID', 'Parent have no ID')], max_length=100, null=True, verbose_name='Parent ID type'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='parent_individual_case_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Individual Case number'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='parent_individual_case_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Individual Case number confirm'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='parent_national_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Syrian / Lebanese ID number '),
        ),
        migrations.AddField(
            model_name='cbece',
            name='parent_national_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Syrian / Lebanese ID number confirm'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='source_of_identification',
            field=models.CharField(blank=True, choices=[('Family walked in to NGO', 'Family walked in to NGO'), ('Referral from another NGO or municipality', 'Referral from another NGO or municipality'), ('Direct outreach', 'Direct outreach'), ('List database', 'List database')], max_length=100, null=True, verbose_name='Source of identification of the child'),
        ),
        migrations.AddField(
            model_name='rs',
            name='no_child_id_confirmation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='rs',
            name='no_parent_id_confirmation',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='rs',
            name='parent_case_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Case number'),
        ),
        migrations.AddField(
            model_name='rs',
            name='parent_case_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Case number confirm'),
        ),
        migrations.AddField(
            model_name='rs',
            name='parent_id_type',
            field=models.CharField(blank=True, choices=[('UNHCR Registered', 'UNHCR Registered'), ('Syrian national ID', 'Syrian national ID'), ('Lebanese national ID', 'Lebanese national ID'), ('Parent have no ID', 'Parent have no ID')], max_length=100, null=True, verbose_name='Parent ID type'),
        ),
        migrations.AddField(
            model_name='rs',
            name='parent_individual_case_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Individual Case number'),
        ),
        migrations.AddField(
            model_name='rs',
            name='parent_individual_case_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Individual Case number confirm'),
        ),
        migrations.AddField(
            model_name='rs',
            name='parent_national_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Syrian / Lebanese ID number '),
        ),
        migrations.AddField(
            model_name='rs',
            name='parent_national_number_confirm',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Syrian / Lebanese ID number confirm'),
        ),
        migrations.AddField(
            model_name='rs',
            name='source_of_identification',
            field=models.CharField(blank=True, choices=[('Family walked in to NGO', 'Family walked in to NGO'), ('Referral from another NGO or municipality', 'Referral from another NGO or municipality'), ('Direct outreach', 'Direct outreach'), ('List database', 'List database')], max_length=100, null=True, verbose_name='Source of identification of the child'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='id_type',
            field=models.CharField(blank=True, choices=[('UNHCR Registered', 'UNHCR Registered'), ('UNHCR Recorded', 'UNHCR Recorded'), ('Syrian national ID', 'Syrian national ID'), ('Lebanese national ID', 'Lebanese national ID'), ('Child have no ID', 'Child have no ID')], max_length=100, null=True, verbose_name='Child ID type'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='id_type',
            field=models.CharField(blank=True, choices=[('UNHCR Registered', 'UNHCR Registered'), ('UNHCR Recorded', 'UNHCR Recorded'), ('Syrian national ID', 'Syrian national ID'), ('Lebanese national ID', 'Lebanese national ID'), ('Child have no ID', 'Child have no ID')], max_length=100, null=True, verbose_name='Child ID type'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='id_type',
            field=models.CharField(blank=True, choices=[('UNHCR Registered', 'UNHCR Registered'), ('UNHCR Recorded', 'UNHCR Recorded'), ('Syrian national ID', 'Syrian national ID'), ('Lebanese national ID', 'Lebanese national ID'), ('Child have no ID', 'Child have no ID')], max_length=100, null=True, verbose_name='Child ID type'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='id_type',
            field=models.CharField(blank=True, choices=[('UNHCR Registered', 'UNHCR Registered'), ('UNHCR Recorded', 'UNHCR Recorded'), ('Syrian national ID', 'Syrian national ID'), ('Lebanese national ID', 'Lebanese national ID'), ('Child have no ID', 'Child have no ID')], max_length=100, null=True, verbose_name='Child ID type'),
        ),
    ]
