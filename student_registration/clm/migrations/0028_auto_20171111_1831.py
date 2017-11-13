# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-11 16:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0027_auto_20171109_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bln',
            name='learning_result',
            field=models.CharField(blank=True, choices=[('', ' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'), ('repeat_level', 'Repeat level'), ('attended_public_school', '\u064a\u062d\u0636\u0631 \u0641\u064a \u0645\u062f\u0631\u0633\u0629 \u0631\u0633\u0645\u064a\u0629'), ('referred_to_alp', 'referred to ALP'), ('ready_to_alp_but_not_possible', 'Ready for ALP but referral is not possible'), ('reenrolled_in_alp', 'Re-register on another round of BLN'), ('not_enrolled_any_program', 'Not enrolled in any educational program'), ('dropout', '\u062a\u0633\u0631\u0628 \u0645\u0646 \u0627\u0644\u062f\u0631\u0627\u0633\u0629')], max_length=100, null=True, verbose_name=' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'),
        ),
        migrations.AlterField(
            model_name='rs',
            name='learning_result',
            field=models.CharField(blank=True, choices=[('', ' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'), ('repeat_level', 'Repeat level'), ('dropout', '\u062a\u0633\u0631\u0628 \u0645\u0646 \u0627\u0644\u062f\u0631\u0627\u0633\u0629'), ('graduated_next_level', '\u0631\u0641\u0639 \u0625\u0644\u0649 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u062a\u0627\u0644\u064a')], max_length=100, null=True, verbose_name=' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'),
        ),
    ]
