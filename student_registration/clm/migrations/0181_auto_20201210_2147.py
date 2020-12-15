# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-12-10 19:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0180_auto_20201203_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abln',
            name='barriers_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='covid_parent_attended_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='followup_parent_attended_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='learning_result',
            field=models.CharField(blank=True, choices=[('', ' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'), ('graduated_to_abln_next_level', '\u0631\u0641\u0639 \u0625\u0644\u0649 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u062a\u0627\u0644\u064a'), ('graduated_to_abln_next_round_same_level', '\u0625\u0643\u0645\u0627\u0644 \u0641\u064a \u0646\u0641\u0633 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0641\u064a \u0627\u0644\u062f\u0648\u0631\u0629 \u0627\u0644\u0642\u0627\u062f\u0645\u0629'), ('graduated_to_abln_next_round_higher_level', '\u064a\u0631\u0641\u0639 \u0625\u0627\u0644\u0649 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u0623\u0639\u0644\u0649 \u0641\u064a \u0627\u0644\u062f\u0648\u0631\u0629 \u0627\u0644\u0642\u0627\u062f\u0645\u0629'), ('referred_to_bln', ' \u0627\u0644\u0623\u062d\u0627\u0644\u0629 \u0645\u0646 ABLN \u0625\u0644\u0649 \u0628\u0631\u0646\u0627\u0645\u062c BLN'), ('referred_to_ybln', '\u0627\u0644\u0623\u062d\u0627\u0644\u0629 \u0625\u0627\u0644\u0649 \u0628\u0631\u0646\u0627\u0645\u062c \u0627\u0644\u0645\u0631\u0627\u0647\u0642\u064a\u0646 (YBLN)'), ('referred_to_alp', '\u0623\u062d\u064a\u0644 \u0625\u0644\u0649 \u0628\u0631\u0646\u0627\u0645\u062c ALP'), ('referred_to_cbt', '\u0623\u062d\u064a\u0644 \u0625\u0644\u0649 \u0628\u0631\u0646\u0627\u0645\u062c CBT'), ('dropout', '\u0627\u0644\u062a\u0633\u0631\u0628 \u0645\u0646 \u0627\u0644\u062f\u0648\u0631\u0629')], max_length=100, null=True, verbose_name=' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='pss_parent_attended_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='reasons_not_engaged_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='barriers_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='covid_parent_attended_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='followup_parent_attended_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='learning_result',
            field=models.CharField(blank=True, choices=[('', ' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'), ('graduated_to_bln_next_level', '\u0631\u0641\u0639 \u0625\u0644\u0649 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u062a\u0627\u0644\u064a'), ('graduated_to_bln_next_round_same_level', '\u0625\u0643\u0645\u0627\u0644 \u0641\u064a \u0646\u0641\u0633 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0641\u064a \u0627\u0644\u062f\u0648\u0631\u0629 \u0627\u0644\u0642\u0627\u062f\u0645\u0629'), ('graduated_to_bln_next_round_higher_level', '\u064a\u0631\u0641\u0639 \u0625\u0627\u0644\u0649 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u0623\u0639\u0644\u0649 \u0641\u064a \u0627\u0644\u062f\u0648\u0631\u0629 \u0627\u0644\u0642\u0627\u062f\u0645\u0629'), ('referred_to_alp', '\u0623\u062d\u064a\u0644 \u0625\u0644\u0649 \u0628\u0631\u0646\u0627\u0645\u062c ALP'), ('referred_public_school', '\u064a\u0631\u0641\u0639 \u0627\u0644\u0649 \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0627\u0644\u0631\u0633\u0645\u064a'), ('referred_to_tvet', '\u0627\u0644\u0623\u062d\u0627\u0644\u0629 \u0627\u0644\u0649 \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0627\u0644\u0645\u0647\u0646\u064a \u0648 \u0627\u0644\u062a\u0642\u0646\u064a (TVET)'), ('referred_to_ybln', '\u0627\u0644\u0623\u062d\u0627\u0644\u0629 \u0625\u0627\u0644\u0649 \u0628\u0631\u0646\u0627\u0645\u062c \u0627\u0644\u0645\u0631\u0627\u0647\u0642\u064a\u0646 (YBLN)'), ('dropout', '\u0627\u0644\u062a\u0633\u0631\u0628 \u0645\u0646 \u0627\u0644\u062f\u0648\u0631\u0629')], max_length=100, null=True, verbose_name=' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='pss_parent_attended_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='reasons_not_engaged_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='barriers_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='covid_parent_attended_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='followup_parent_attended_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='learning_result',
            field=models.CharField(blank=True, choices=[('', '----------'), ('graduated_to_cbece_next_level', '\u0631\u0641\u0639 \u0625\u0644\u0649 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u062a\u0627\u0644\u064a'), ('graduated_to_cbece_next_round_same_level', '\u0625\u0643\u0645\u0627\u0644 \u0641\u064a \u0646\u0641\u0633 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0641\u064a \u0627\u0644\u062f\u0648\u0631\u0629 \u0627\u0644\u0642\u0627\u062f\u0645\u0629'), ('graduated_to_cbece_next_round_higher_level', '\u064a\u0631\u0641\u0639 \u0625\u0627\u0644\u0649 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u0623\u0639\u0644\u0649 \u0641\u064a \u0627\u0644\u062f\u0648\u0631\u0629 \u0627\u0644\u0642\u0627\u062f\u0645\u0629 (\u0627\u0644\u0645\u0633\u062a\u0648\u0649 3)'), ('referred_to_alp', '\u0623\u062d\u064a\u0644 \u0625\u0644\u0649 \u0628\u0631\u0646\u0627\u0645\u062c ALP'), ('referred_public_school', '\u064a\u0631\u0641\u0639 \u0627\u0644\u0649 \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0627\u0644\u0631\u0633\u0645\u064a \u0627\u0644\u0635\u0641 \u0627\u0644\u0623\u0648\u0644'), ('referred_to_tvet', '\u0627\u0644\u0623\u062d\u0627\u0644\u0629 \u0627\u0644\u0649 \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0627\u0644\u0645\u0647\u0646\u064a \u0648 \u0627\u0644\u062a\u0642\u0646\u064a (TVET)'), ('referred_to_ycbece', 'Referred to YCBECE'), ('dropout', '\u0627\u0644\u062a\u0633\u0631\u0628 \u0645\u0646 \u0627\u0644\u062f\u0648\u0631\u0629')], max_length=100, null=True, verbose_name=' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='pss_parent_attended_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='reasons_not_engaged_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='inclusion',
            name='learning_result',
            field=models.CharField(blank=True, choices=[('graduated_to_abln_next_round_same_level', '\u0625\u0643\u0645\u0627\u0644 \u0641\u064a \u0646\u0641\u0633 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0641\u064a \u0627\u0644\u062f\u0648\u0631\u0629 \u0627\u0644\u0642\u0627\u062f\u0645\u0629'), ('graduated_to_abln_next_round_higher_level', '\u064a\u0631\u0641\u0639 \u0625\u0627\u0644\u0649 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u0623\u0639\u0644\u0649 \u0641\u064a \u0627\u0644\u062f\u0648\u0631\u0629 \u0627\u0644\u0642\u0627\u062f\u0645\u0629'), ('referred_to_bln', ' \u0627\u0644\u0623\u062d\u0627\u0644\u0629 \u0645\u0646 ABLN \u0625\u0644\u0649 \u0628\u0631\u0646\u0627\u0645\u062c BLN'), ('referred_to_ybln', '\u0627\u0644\u0623\u062d\u0627\u0644\u0629 \u0625\u0627\u0644\u0649 \u0628\u0631\u0646\u0627\u0645\u062c \u0627\u0644\u0645\u0631\u0627\u0647\u0642\u064a\u0646 (YBLN)'), ('referred_to_cbt', '\u0623\u062d\u064a\u0644 \u0625\u0644\u0649 \u0628\u0631\u0646\u0627\u0645\u062c CBT')], max_length=100, null=True, verbose_name=' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='barriers_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='covid_parent_attended_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='followup_parent_attended_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='pss_parent_attended_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='reasons_not_engaged_other',
            field=models.TextField(blank=True, null=True, verbose_name='\u064a\u0631\u062c\u0649 \u0627\u0644\u062a\u062d\u062f\u064a\u062f'),
        ),
    ]
