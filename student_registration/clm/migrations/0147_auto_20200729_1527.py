# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-07-29 12:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0146_auto_20200729_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abln',
            name='covid_message_how_often',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], null=True, verbose_name=' \u0643\u0645 \u0645\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='covid_parents_message_how_often',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], null=True, verbose_name=' \u0643\u0645 \u0645\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='follow_up_done',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='\u0647\u0644 \u062a\u0645 \u0625\u062c\u0631\u0627\u0621 \u0623\u064a \u0645\u062a\u0627\u0628\u0639\u0629 \u0644\u0636\u0645\u0627\u0646 \u062a\u0644\u0642\u064a \u0627\u0644\u0631\u0633\u0627\u0626\u0644 \u0648\u0641\u0647\u0645\u0647\u0627 \u0648\u0627\u0639\u062a\u0645\u0627\u062f\u0647\u0627 \u0628\u0634\u0643\u0644 \u062c\u064a\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='follow_up_done_with_who',
            field=models.CharField(blank=True, choices=[('child', '\u0627\u0644\u0637\u0641\u0644'), ('caregiver', '\u0645\u0642\u062f\u0645 \u0627\u0644\u0631\u0639\u0627\u064a\u0629'), ('childand_or_caregiver', '\u0627\u0644\u0641\u0631\u0646\u0633\u064a\u0629/\u0627\u0644\u0639\u0631\u0628\u064a\u0629')], max_length=50, null=True, verbose_name='\u0645\u0639 \u0645\u0646 \u062a\u0645 \u0627\u0644\u062a\u0648\u0627\u0635\u0644 \u0627\u0644\u0637\u0641\u0644 \u0645\u0639/\u0627\u0648 \u0645\u0642\u062f\u0645 \u0627\u0644\u0631\u0639\u0627\u064a\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='meet_learning_outcomes',
            field=models.CharField(blank=True, choices=[('hundred', '100%'), ('seventy_five', '75%'), ('fifty', '50%'), ('twenty_five', '25%'), ('less_than_twenty_five', '\u0623\u0642\u0644 \u0645\u0646 25%')], max_length=100, null=True, verbose_name='\u0643\u064a\u0641 \u062a\u0642\u064a\u064a\u0645 \u0642\u062f\u0631\u0629 \u0627\u0644\u0637\u0641\u0644  \u0641\u064a \u0641\u0647\u0645 \u0627\u0644\u0645\u0646\u0647\u062c \u0627\u0644\u062a\u0639\u0644\u064a\u0645\u064a \u0627\u0644\u0645\u0639\u062a\u0645\u062f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='parent_learning_support_rate',
            field=models.CharField(blank=True, choices=[('hundred', '100%'), ('seventy_five', '75%'), ('fifty', '50%'), ('twenty_five', '25%'), ('less_than_twenty_five', '\u0623\u0642\u0644 \u0645\u0646 25%')], max_length=100, null=True, verbose_name='\u0643\u064a\u0641 \u062a\u0642\u064a\u0645 \u062f\u0639\u0645 \u0627\u0623\u0647\u0644 \u0627\u0644\u0637\u0641\u0644 \u0641\u064a \u062a\u0642\u062f\u064a\u0645 \u0627\u0644\u0645\u0633\u0627\u0639\u062f\u0629 \u0627\u0644\u0645\u0637\u0644\u0648\u0628\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='reliable_internet',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627'), ('sometimes', '\u0628\u0639\u0636 \u0627\u0644\u0623\u0648\u0642\u0627\u062a')], max_length=10, null=True, verbose_name='\u0647\u0644  \u062e\u062f\u0645\u0629 \u0625\u0646\u062a\u0631\u0646\u062a \u0645\u062a\u0648\u0641\u0631\u0629 \u0644\u0644\u0623\u0647\u0644 \u0641\u064a \u0645\u0646\u0637\u0642\u062a\u0647\u0645 \u0623\u062b\u0646\u0627\u0621 \u0627\u0644\u062a\u0639\u0644\u0645 \u0639\u0646 \u0628\u0639\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='abln',
            name='remote_learning_engagement',
            field=models.CharField(blank=True, choices=[('hundred', '100%'), ('seventy_five', '75%'), ('fifty', '50%'), ('twenty_five', '25%'), ('less_than_twenty_five', '\u0623\u0642\u0644 \u0645\u0646 25%')], max_length=100, null=True, verbose_name='\u0645\u0639\u062f\u0644 \u0627\u0646\u062e\u0631\u0627\u0637 \u0627\u0644\u0637\u0641\u0644 \u0641\u064a \u0627\u0644\u062a\u0639\u0644\u0645 \u0639\u0646 \u0628\u0639\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='covid_message_how_often',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], null=True, verbose_name=' \u0643\u0645 \u0645\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='covid_parents_message_how_often',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], null=True, verbose_name=' \u0643\u0645 \u0645\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='follow_up_done',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='\u0647\u0644 \u062a\u0645 \u0625\u062c\u0631\u0627\u0621 \u0623\u064a \u0645\u062a\u0627\u0628\u0639\u0629 \u0644\u0636\u0645\u0627\u0646 \u062a\u0644\u0642\u064a \u0627\u0644\u0631\u0633\u0627\u0626\u0644 \u0648\u0641\u0647\u0645\u0647\u0627 \u0648\u0627\u0639\u062a\u0645\u0627\u062f\u0647\u0627 \u0628\u0634\u0643\u0644 \u062c\u064a\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='follow_up_done_with_who',
            field=models.CharField(blank=True, choices=[('child', '\u0627\u0644\u0637\u0641\u0644'), ('caregiver', '\u0645\u0642\u062f\u0645 \u0627\u0644\u0631\u0639\u0627\u064a\u0629'), ('childand_or_caregiver', '\u0627\u0644\u0641\u0631\u0646\u0633\u064a\u0629/\u0627\u0644\u0639\u0631\u0628\u064a\u0629')], max_length=50, null=True, verbose_name='\u0645\u0639 \u0645\u0646 \u062a\u0645 \u0627\u0644\u062a\u0648\u0627\u0635\u0644 \u0627\u0644\u0637\u0641\u0644 \u0645\u0639/\u0627\u0648 \u0645\u0642\u062f\u0645 \u0627\u0644\u0631\u0639\u0627\u064a\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='meet_learning_outcomes',
            field=models.CharField(blank=True, choices=[('hundred', '100%'), ('seventy_five', '75%'), ('fifty', '50%'), ('twenty_five', '25%'), ('less_than_twenty_five', '\u0623\u0642\u0644 \u0645\u0646 25%')], max_length=100, null=True, verbose_name='\u0643\u064a\u0641 \u062a\u0642\u064a\u064a\u0645 \u0642\u062f\u0631\u0629 \u0627\u0644\u0637\u0641\u0644  \u0641\u064a \u0641\u0647\u0645 \u0627\u0644\u0645\u0646\u0647\u062c \u0627\u0644\u062a\u0639\u0644\u064a\u0645\u064a \u0627\u0644\u0645\u0639\u062a\u0645\u062f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='parent_learning_support_rate',
            field=models.CharField(blank=True, choices=[('hundred', '100%'), ('seventy_five', '75%'), ('fifty', '50%'), ('twenty_five', '25%'), ('less_than_twenty_five', '\u0623\u0642\u0644 \u0645\u0646 25%')], max_length=100, null=True, verbose_name='\u0643\u064a\u0641 \u062a\u0642\u064a\u0645 \u062f\u0639\u0645 \u0627\u0623\u0647\u0644 \u0627\u0644\u0637\u0641\u0644 \u0641\u064a \u062a\u0642\u062f\u064a\u0645 \u0627\u0644\u0645\u0633\u0627\u0639\u062f\u0629 \u0627\u0644\u0645\u0637\u0644\u0648\u0628\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='reliable_internet',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627'), ('sometimes', '\u0628\u0639\u0636 \u0627\u0644\u0623\u0648\u0642\u0627\u062a')], max_length=10, null=True, verbose_name='\u0647\u0644  \u062e\u062f\u0645\u0629 \u0625\u0646\u062a\u0631\u0646\u062a \u0645\u062a\u0648\u0641\u0631\u0629 \u0644\u0644\u0623\u0647\u0644 \u0641\u064a \u0645\u0646\u0637\u0642\u062a\u0647\u0645 \u0623\u062b\u0646\u0627\u0621 \u0627\u0644\u062a\u0639\u0644\u0645 \u0639\u0646 \u0628\u0639\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='bln',
            name='remote_learning_engagement',
            field=models.CharField(blank=True, choices=[('hundred', '100%'), ('seventy_five', '75%'), ('fifty', '50%'), ('twenty_five', '25%'), ('less_than_twenty_five', '\u0623\u0642\u0644 \u0645\u0646 25%')], max_length=100, null=True, verbose_name='\u0645\u0639\u062f\u0644 \u0627\u0646\u062e\u0631\u0627\u0637 \u0627\u0644\u0637\u0641\u0644 \u0641\u064a \u0627\u0644\u062a\u0639\u0644\u0645 \u0639\u0646 \u0628\u0639\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='covid_message_how_often',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], null=True, verbose_name=' \u0643\u0645 \u0645\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='covid_parents_message_how_often',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], null=True, verbose_name=' \u0643\u0645 \u0645\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='follow_up_done',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='\u0647\u0644 \u062a\u0645 \u0625\u062c\u0631\u0627\u0621 \u0623\u064a \u0645\u062a\u0627\u0628\u0639\u0629 \u0644\u0636\u0645\u0627\u0646 \u062a\u0644\u0642\u064a \u0627\u0644\u0631\u0633\u0627\u0626\u0644 \u0648\u0641\u0647\u0645\u0647\u0627 \u0648\u0627\u0639\u062a\u0645\u0627\u062f\u0647\u0627 \u0628\u0634\u0643\u0644 \u062c\u064a\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='follow_up_done_with_who',
            field=models.CharField(blank=True, choices=[('child', '\u0627\u0644\u0637\u0641\u0644'), ('caregiver', '\u0645\u0642\u062f\u0645 \u0627\u0644\u0631\u0639\u0627\u064a\u0629'), ('childand_or_caregiver', '\u0627\u0644\u0641\u0631\u0646\u0633\u064a\u0629/\u0627\u0644\u0639\u0631\u0628\u064a\u0629')], max_length=50, null=True, verbose_name='\u0645\u0639 \u0645\u0646 \u062a\u0645 \u0627\u0644\u062a\u0648\u0627\u0635\u0644 \u0627\u0644\u0637\u0641\u0644 \u0645\u0639/\u0627\u0648 \u0645\u0642\u062f\u0645 \u0627\u0644\u0631\u0639\u0627\u064a\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='meet_learning_outcomes',
            field=models.CharField(blank=True, choices=[('hundred', '100%'), ('seventy_five', '75%'), ('fifty', '50%'), ('twenty_five', '25%'), ('less_than_twenty_five', '\u0623\u0642\u0644 \u0645\u0646 25%')], max_length=100, null=True, verbose_name='\u0643\u064a\u0641 \u062a\u0642\u064a\u064a\u0645 \u0642\u062f\u0631\u0629 \u0627\u0644\u0637\u0641\u0644  \u0641\u064a \u0641\u0647\u0645 \u0627\u0644\u0645\u0646\u0647\u062c \u0627\u0644\u062a\u0639\u0644\u064a\u0645\u064a \u0627\u0644\u0645\u0639\u062a\u0645\u062f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='parent_learning_support_rate',
            field=models.CharField(blank=True, choices=[('hundred', '100%'), ('seventy_five', '75%'), ('fifty', '50%'), ('twenty_five', '25%'), ('less_than_twenty_five', '\u0623\u0642\u0644 \u0645\u0646 25%')], max_length=100, null=True, verbose_name='\u0643\u064a\u0641 \u062a\u0642\u064a\u0645 \u062f\u0639\u0645 \u0627\u0623\u0647\u0644 \u0627\u0644\u0637\u0641\u0644 \u0641\u064a \u062a\u0642\u062f\u064a\u0645 \u0627\u0644\u0645\u0633\u0627\u0639\u062f\u0629 \u0627\u0644\u0645\u0637\u0644\u0648\u0628\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='reliable_internet',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627'), ('sometimes', '\u0628\u0639\u0636 \u0627\u0644\u0623\u0648\u0642\u0627\u062a')], max_length=10, null=True, verbose_name='\u0647\u0644  \u062e\u062f\u0645\u0629 \u0625\u0646\u062a\u0631\u0646\u062a \u0645\u062a\u0648\u0641\u0631\u0629 \u0644\u0644\u0623\u0647\u0644 \u0641\u064a \u0645\u0646\u0637\u0642\u062a\u0647\u0645 \u0623\u062b\u0646\u0627\u0621 \u0627\u0644\u062a\u0639\u0644\u0645 \u0639\u0646 \u0628\u0639\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='cbece',
            name='remote_learning_engagement',
            field=models.CharField(blank=True, choices=[('hundred', '100%'), ('seventy_five', '75%'), ('fifty', '50%'), ('twenty_five', '25%'), ('less_than_twenty_five', '\u0623\u0642\u0644 \u0645\u0646 25%')], max_length=100, null=True, verbose_name='\u0645\u0639\u062f\u0644 \u0627\u0646\u062e\u0631\u0627\u0637 \u0627\u0644\u0637\u0641\u0644 \u0641\u064a \u0627\u0644\u062a\u0639\u0644\u0645 \u0639\u0646 \u0628\u0639\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='covid_message_how_often',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], null=True, verbose_name=' \u0643\u0645 \u0645\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='covid_parents_message_how_often',
            field=models.IntegerField(blank=True, choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9)], null=True, verbose_name=' \u0643\u0645 \u0645\u0631\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='follow_up_done',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627')], max_length=10, null=True, verbose_name='\u0647\u0644 \u062a\u0645 \u0625\u062c\u0631\u0627\u0621 \u0623\u064a \u0645\u062a\u0627\u0628\u0639\u0629 \u0644\u0636\u0645\u0627\u0646 \u062a\u0644\u0642\u064a \u0627\u0644\u0631\u0633\u0627\u0626\u0644 \u0648\u0641\u0647\u0645\u0647\u0627 \u0648\u0627\u0639\u062a\u0645\u0627\u062f\u0647\u0627 \u0628\u0634\u0643\u0644 \u062c\u064a\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='follow_up_done_with_who',
            field=models.CharField(blank=True, choices=[('child', '\u0627\u0644\u0637\u0641\u0644'), ('caregiver', '\u0645\u0642\u062f\u0645 \u0627\u0644\u0631\u0639\u0627\u064a\u0629'), ('childand_or_caregiver', '\u0627\u0644\u0641\u0631\u0646\u0633\u064a\u0629/\u0627\u0644\u0639\u0631\u0628\u064a\u0629')], max_length=50, null=True, verbose_name='\u0645\u0639 \u0645\u0646 \u062a\u0645 \u0627\u0644\u062a\u0648\u0627\u0635\u0644 \u0627\u0644\u0637\u0641\u0644 \u0645\u0639/\u0627\u0648 \u0645\u0642\u062f\u0645 \u0627\u0644\u0631\u0639\u0627\u064a\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='meet_learning_outcomes',
            field=models.CharField(blank=True, choices=[('hundred', '100%'), ('seventy_five', '75%'), ('fifty', '50%'), ('twenty_five', '25%'), ('less_than_twenty_five', '\u0623\u0642\u0644 \u0645\u0646 25%')], max_length=100, null=True, verbose_name='\u0643\u064a\u0641 \u062a\u0642\u064a\u064a\u0645 \u0642\u062f\u0631\u0629 \u0627\u0644\u0637\u0641\u0644  \u0641\u064a \u0641\u0647\u0645 \u0627\u0644\u0645\u0646\u0647\u062c \u0627\u0644\u062a\u0639\u0644\u064a\u0645\u064a \u0627\u0644\u0645\u0639\u062a\u0645\u062f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='parent_learning_support_rate',
            field=models.CharField(blank=True, choices=[('hundred', '100%'), ('seventy_five', '75%'), ('fifty', '50%'), ('twenty_five', '25%'), ('less_than_twenty_five', '\u0623\u0642\u0644 \u0645\u0646 25%')], max_length=100, null=True, verbose_name='\u0643\u064a\u0641 \u062a\u0642\u064a\u0645 \u062f\u0639\u0645 \u0627\u0623\u0647\u0644 \u0627\u0644\u0637\u0641\u0644 \u0641\u064a \u062a\u0642\u062f\u064a\u0645 \u0627\u0644\u0645\u0633\u0627\u0639\u062f\u0629 \u0627\u0644\u0645\u0637\u0644\u0648\u0628\u0629\u061f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='reliable_internet',
            field=models.CharField(blank=True, choices=[('yes', '\u0646\u0639\u0645'), ('no', '\u0643\u0644\u0627'), ('sometimes', '\u0628\u0639\u0636 \u0627\u0644\u0623\u0648\u0642\u0627\u062a')], max_length=10, null=True, verbose_name='\u0647\u0644  \u062e\u062f\u0645\u0629 \u0625\u0646\u062a\u0631\u0646\u062a \u0645\u062a\u0648\u0641\u0631\u0629 \u0644\u0644\u0623\u0647\u0644 \u0641\u064a \u0645\u0646\u0637\u0642\u062a\u0647\u0645 \u0623\u062b\u0646\u0627\u0621 \u0627\u0644\u062a\u0639\u0644\u0645 \u0639\u0646 \u0628\u0639\u062f\u061f'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='remote_learning_engagement',
            field=models.CharField(blank=True, choices=[('hundred', '100%'), ('seventy_five', '75%'), ('fifty', '50%'), ('twenty_five', '25%'), ('less_than_twenty_five', '\u0623\u0642\u0644 \u0645\u0646 25%')], max_length=100, null=True, verbose_name='\u0645\u0639\u062f\u0644 \u0627\u0646\u062e\u0631\u0627\u0637 \u0627\u0644\u0637\u0641\u0644 \u0641\u064a \u0627\u0644\u062a\u0639\u0644\u0645 \u0639\u0646 \u0628\u0639\u062f\u061f'),
        ),
    ]
