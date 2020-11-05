# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2020-11-05 20:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0170_auto_20201030_2325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cbece',
            name='learning_result',
            field=models.CharField(blank=True, choices=[('', '----------'), ('graduated_to_cbece_next_level', '\u0631\u0641\u0639 \u0625\u0644\u0649 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u062a\u0627\u0644\u064a'), ('graduated_to_cbece_next_round_same_level', '\u0625\u0643\u0645\u0627\u0644 \u0641\u064a \u0646\u0641\u0633 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0641\u064a \u0627\u0644\u062f\u0648\u0631\u0629 \u0627\u0644\u0642\u0627\u062f\u0645\u0629'), ('graduated_to_cbece_next_round_higher_level', '\u064a\u0631\u0641\u0639 \u0625\u0627\u0644\u0649 \u0627\u0644\u0645\u0633\u062a\u0648\u0649 \u0627\u0644\u0623\u0639\u0644\u0649 \u0641\u064a \u0627\u0644\u062f\u0648\u0631\u0629 \u0627\u0644\u0642\u0627\u062f\u0645\u0629'), ('referred_to_alp', '\u0623\u062d\u064a\u0644 \u0625\u0644\u0649 \u0628\u0631\u0646\u0627\u0645\u062c ALP'), ('referred_public_school', '\u0627\u0644\u0623\u062d\u0627\u0644\u0629 \u0625\u0644\u0649 \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0627\u0644\u0631\u0633\u0645\u064a'), ('referred_to_tvet', '\u0627\u0644\u0623\u062d\u0627\u0644\u0629 \u0627\u0644\u0649 \u0627\u0644\u062a\u0639\u0644\u064a\u0645 \u0627\u0644\u0645\u0647\u0646\u064a \u0648 \u0627\u0644\u062a\u0642\u0646\u064a (TVET)'), ('referred_to_ycbece', 'Referred to YCBECE'), ('dropout', '\u0627\u0644\u062a\u0633\u0631\u0628 \u0645\u0646 \u0627\u0644\u062f\u0648\u0631\u0629')], max_length=100, null=True, verbose_name=' \u0646\u062a\u064a\u062c\u0629 \u0627\u0644\u062a\u0639\u0644\u0645'),
        ),
    ]
