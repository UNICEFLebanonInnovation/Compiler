# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-03-09 10:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0086_auto_20200309_1236'),
    ]

    operations = [
        migrations.AddField(
            model_name='abln',
            name='have_labour_single_selection',
            field=models.CharField(blank=True, choices=[('no', '\u0643\u0644\u0627'), ('yes_morning', '\u0646\u0639\u0645 - \u0642\u0628\u0644 \u0627\u0644\u0638\u0647\u0631'), ('yes_afternoon', '\u0646\u0639\u0645 - \u0628\u0639\u062f \u0627\u0644\u0638\u0647\u0631'), ('yes_all_day', '\u0646\u0639\u0645 - \u0643\u0644 \u0627\u0644\u0646\u0647\u0627\u0631')], max_length=100, null=True, verbose_name='\u0647\u0644 \u064a\u0634\u0627\u0631\u0643 \u0627\u0644\u0637\u0641\u0644 \u0641\u064a \u0639\u0645\u0644\u061f'),
        ),
        migrations.AddField(
            model_name='abln',
            name='labours_single_selection',
            field=models.CharField(blank=True, choices=[('agriculture', '\u0627\u0644\u0632\u0631\u0627\u0639\u0629'), ('building', '\u0627\u0644\u0628\u0646\u0627\u0621'), ('manufacturing', '\u0627\u0644\u062a\u0635\u0646\u064a\u0639'), ('retail_store', '\u0627\u0644\u0628\u064a\u0639 \u0628\u0627\u0644\u0645\u0641\u0631\u0642 / \u0645\u062d\u0644'), ('begging', '\u062a\u0633\u0648\u0644'), ('other_many_other', ' \u062e\u062f\u0645\u0627\u062a \u0645\u062e\u062a\u0644\u0641\u0629 (\u0641\u0646\u062f\u0642\u060c \u0645\u0637\u0639\u0645\u060c \u0646\u0642\u0644\u060c \u062e\u062f\u0645\u0627\u062a \u0634\u062e\u0635\u064a\u0629 \u0645\u062b\u0644 \u0627\u0644\u062a\u0646\u0638\u064a\u0641\u060c \u0627\u0644\u0639\u0646\u0627\u064a\u0629 \u0628\u0627\u0644\u0634\u0639\u0631\u060c \u0627\u0644\u0637\u0628\u062e \u0648\u0627\u0644\u0625\u0639\u062a\u0646\u0627\u0621 \u0628\u0627\u0644\u0623\u0637\u0641\u0627\u0644)')], max_length=100, null=True, verbose_name='\u0645\u0627 \u0647\u0648 \u0646\u0648\u0639 \u0627\u0644\u0639\u0645\u0644 \u061f'),
        ),
        migrations.AddField(
            model_name='bln',
            name='have_labour_single_selection',
            field=models.CharField(blank=True, choices=[('no', '\u0643\u0644\u0627'), ('yes_morning', '\u0646\u0639\u0645 - \u0642\u0628\u0644 \u0627\u0644\u0638\u0647\u0631'), ('yes_afternoon', '\u0646\u0639\u0645 - \u0628\u0639\u062f \u0627\u0644\u0638\u0647\u0631'), ('yes_all_day', '\u0646\u0639\u0645 - \u0643\u0644 \u0627\u0644\u0646\u0647\u0627\u0631')], max_length=100, null=True, verbose_name='\u0647\u0644 \u064a\u0634\u0627\u0631\u0643 \u0627\u0644\u0637\u0641\u0644 \u0641\u064a \u0639\u0645\u0644\u061f'),
        ),
        migrations.AddField(
            model_name='bln',
            name='labours_single_selection',
            field=models.CharField(blank=True, choices=[('agriculture', '\u0627\u0644\u0632\u0631\u0627\u0639\u0629'), ('building', '\u0627\u0644\u0628\u0646\u0627\u0621'), ('manufacturing', '\u0627\u0644\u062a\u0635\u0646\u064a\u0639'), ('retail_store', '\u0627\u0644\u0628\u064a\u0639 \u0628\u0627\u0644\u0645\u0641\u0631\u0642 / \u0645\u062d\u0644'), ('begging', '\u062a\u0633\u0648\u0644'), ('other_many_other', ' \u062e\u062f\u0645\u0627\u062a \u0645\u062e\u062a\u0644\u0641\u0629 (\u0641\u0646\u062f\u0642\u060c \u0645\u0637\u0639\u0645\u060c \u0646\u0642\u0644\u060c \u062e\u062f\u0645\u0627\u062a \u0634\u062e\u0635\u064a\u0629 \u0645\u062b\u0644 \u0627\u0644\u062a\u0646\u0638\u064a\u0641\u060c \u0627\u0644\u0639\u0646\u0627\u064a\u0629 \u0628\u0627\u0644\u0634\u0639\u0631\u060c \u0627\u0644\u0637\u0628\u062e \u0648\u0627\u0644\u0625\u0639\u062a\u0646\u0627\u0621 \u0628\u0627\u0644\u0623\u0637\u0641\u0627\u0644)')], max_length=100, null=True, verbose_name='\u0645\u0627 \u0647\u0648 \u0646\u0648\u0639 \u0627\u0644\u0639\u0645\u0644 \u061f'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='have_labour_single_selection',
            field=models.CharField(blank=True, choices=[('no', '\u0643\u0644\u0627'), ('yes_morning', '\u0646\u0639\u0645 - \u0642\u0628\u0644 \u0627\u0644\u0638\u0647\u0631'), ('yes_afternoon', '\u0646\u0639\u0645 - \u0628\u0639\u062f \u0627\u0644\u0638\u0647\u0631'), ('yes_all_day', '\u0646\u0639\u0645 - \u0643\u0644 \u0627\u0644\u0646\u0647\u0627\u0631')], max_length=100, null=True, verbose_name='\u0647\u0644 \u064a\u0634\u0627\u0631\u0643 \u0627\u0644\u0637\u0641\u0644 \u0641\u064a \u0639\u0645\u0644\u061f'),
        ),
        migrations.AddField(
            model_name='cbece',
            name='labours_single_selection',
            field=models.CharField(blank=True, choices=[('agriculture', '\u0627\u0644\u0632\u0631\u0627\u0639\u0629'), ('building', '\u0627\u0644\u0628\u0646\u0627\u0621'), ('manufacturing', '\u0627\u0644\u062a\u0635\u0646\u064a\u0639'), ('retail_store', '\u0627\u0644\u0628\u064a\u0639 \u0628\u0627\u0644\u0645\u0641\u0631\u0642 / \u0645\u062d\u0644'), ('begging', '\u062a\u0633\u0648\u0644'), ('other_many_other', ' \u062e\u062f\u0645\u0627\u062a \u0645\u062e\u062a\u0644\u0641\u0629 (\u0641\u0646\u062f\u0642\u060c \u0645\u0637\u0639\u0645\u060c \u0646\u0642\u0644\u060c \u062e\u062f\u0645\u0627\u062a \u0634\u062e\u0635\u064a\u0629 \u0645\u062b\u0644 \u0627\u0644\u062a\u0646\u0638\u064a\u0641\u060c \u0627\u0644\u0639\u0646\u0627\u064a\u0629 \u0628\u0627\u0644\u0634\u0639\u0631\u060c \u0627\u0644\u0637\u0628\u062e \u0648\u0627\u0644\u0625\u0639\u062a\u0646\u0627\u0621 \u0628\u0627\u0644\u0623\u0637\u0641\u0627\u0644)')], max_length=100, null=True, verbose_name='\u0645\u0627 \u0647\u0648 \u0646\u0648\u0639 \u0627\u0644\u0639\u0645\u0644 \u061f'),
        ),
        migrations.AddField(
            model_name='rs',
            name='have_labour_single_selection',
            field=models.CharField(blank=True, choices=[('no', '\u0643\u0644\u0627'), ('yes_morning', '\u0646\u0639\u0645 - \u0642\u0628\u0644 \u0627\u0644\u0638\u0647\u0631'), ('yes_afternoon', '\u0646\u0639\u0645 - \u0628\u0639\u062f \u0627\u0644\u0638\u0647\u0631'), ('yes_all_day', '\u0646\u0639\u0645 - \u0643\u0644 \u0627\u0644\u0646\u0647\u0627\u0631')], max_length=100, null=True, verbose_name='\u0647\u0644 \u064a\u0634\u0627\u0631\u0643 \u0627\u0644\u0637\u0641\u0644 \u0641\u064a \u0639\u0645\u0644\u061f'),
        ),
        migrations.AddField(
            model_name='rs',
            name='labours_single_selection',
            field=models.CharField(blank=True, choices=[('agriculture', '\u0627\u0644\u0632\u0631\u0627\u0639\u0629'), ('building', '\u0627\u0644\u0628\u0646\u0627\u0621'), ('manufacturing', '\u0627\u0644\u062a\u0635\u0646\u064a\u0639'), ('retail_store', '\u0627\u0644\u0628\u064a\u0639 \u0628\u0627\u0644\u0645\u0641\u0631\u0642 / \u0645\u062d\u0644'), ('begging', '\u062a\u0633\u0648\u0644'), ('other_many_other', ' \u062e\u062f\u0645\u0627\u062a \u0645\u062e\u062a\u0644\u0641\u0629 (\u0641\u0646\u062f\u0642\u060c \u0645\u0637\u0639\u0645\u060c \u0646\u0642\u0644\u060c \u062e\u062f\u0645\u0627\u062a \u0634\u062e\u0635\u064a\u0629 \u0645\u062b\u0644 \u0627\u0644\u062a\u0646\u0638\u064a\u0641\u060c \u0627\u0644\u0639\u0646\u0627\u064a\u0629 \u0628\u0627\u0644\u0634\u0639\u0631\u060c \u0627\u0644\u0637\u0628\u062e \u0648\u0627\u0644\u0625\u0639\u062a\u0646\u0627\u0621 \u0628\u0627\u0644\u0623\u0637\u0641\u0627\u0644)')], max_length=100, null=True, verbose_name='\u0645\u0627 \u0647\u0648 \u0646\u0648\u0639 \u0627\u0644\u0639\u0645\u0644 \u061f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='source_of_transportation',
            field=models.CharField(blank=True, choices=[('Transportation provided by partner', '\u0627\u0644\u0645\u0648\u0627\u0635\u0644\u0627\u062a \u0645\u0624\u0645\u0646\u0629 \u0645\u0646 \u0627\u0644\u062c\u0645\u0639\u064a\u0629'), ('Walk', '\u0645\u0634\u064a\u0627\u064b'), ('private or parents', '\u0639\u0644\u0649 \u0646\u0641\u0642\u062a\u0647 \u0627\u0644\u062e\u0627\u0635\u0629 / \u0628\u0648\u0627\u0633\u0637\u0629 \u0627\u0644\u0623\u0647\u0644')], max_length=100, null=True, verbose_name='\u0643\u064a\u0641 \u064a\u062d\u0636\u0631 \u0627\u0644\u0637\u0641\u0644 \u0625\u0644\u0649 \u0645\u0631\u0643\u0632 \u0627\u0644\u062c\u0645\u0639\u064a\u0629 \u0644\u0644\u062f\u0648\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='source_of_transportation',
            field=models.CharField(blank=True, choices=[('Transportation provided by partner', '\u0627\u0644\u0645\u0648\u0627\u0635\u0644\u0627\u062a \u0645\u0624\u0645\u0646\u0629 \u0645\u0646 \u0627\u0644\u062c\u0645\u0639\u064a\u0629'), ('Walk', '\u0645\u0634\u064a\u0627\u064b'), ('private or parents', '\u0639\u0644\u0649 \u0646\u0641\u0642\u062a\u0647 \u0627\u0644\u062e\u0627\u0635\u0629 / \u0628\u0648\u0627\u0633\u0637\u0629 \u0627\u0644\u0623\u0647\u0644')], max_length=100, null=True, verbose_name='\u0643\u064a\u0641 \u064a\u062d\u0636\u0631 \u0627\u0644\u0637\u0641\u0644 \u0625\u0644\u0649 \u0645\u0631\u0643\u0632 \u0627\u0644\u062c\u0645\u0639\u064a\u0629 \u0644\u0644\u062f\u0648\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='source_of_transportation',
            field=models.CharField(blank=True, choices=[('Transportation provided by partner', '\u0627\u0644\u0645\u0648\u0627\u0635\u0644\u0627\u062a \u0645\u0624\u0645\u0646\u0629 \u0645\u0646 \u0627\u0644\u062c\u0645\u0639\u064a\u0629'), ('Walk', '\u0645\u0634\u064a\u0627\u064b'), ('private or parents', '\u0639\u0644\u0649 \u0646\u0641\u0642\u062a\u0647 \u0627\u0644\u062e\u0627\u0635\u0629 / \u0628\u0648\u0627\u0633\u0637\u0629 \u0627\u0644\u0623\u0647\u0644')], max_length=100, null=True, verbose_name='\u0643\u064a\u0641 \u064a\u062d\u0636\u0631 \u0627\u0644\u0637\u0641\u0644 \u0625\u0644\u0649 \u0645\u0631\u0643\u0632 \u0627\u0644\u062c\u0645\u0639\u064a\u0629 \u0644\u0644\u062f\u0648\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='source_of_transportation',
            field=models.CharField(blank=True, choices=[('Transportation provided by partner', '\u0627\u0644\u0645\u0648\u0627\u0635\u0644\u0627\u062a \u0645\u0624\u0645\u0646\u0629 \u0645\u0646 \u0627\u0644\u062c\u0645\u0639\u064a\u0629'), ('Walk', '\u0645\u0634\u064a\u0627\u064b'), ('private or parents', '\u0639\u0644\u0649 \u0646\u0641\u0642\u062a\u0647 \u0627\u0644\u062e\u0627\u0635\u0629 / \u0628\u0648\u0627\u0633\u0637\u0629 \u0627\u0644\u0623\u0647\u0644')], max_length=100, null=True, verbose_name='\u0643\u064a\u0641 \u064a\u062d\u0636\u0631 \u0627\u0644\u0637\u0641\u0644 \u0625\u0644\u0649 \u0645\u0631\u0643\u0632 \u0627\u0644\u062c\u0645\u0639\u064a\u0629 \u0644\u0644\u062f\u0648\u0631\u0629\u061f'),
        ),
    ]