# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backends", "0015_exporthistory_add_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="useractivity",
            name="path",
            field=models.TextField(),
        ),
    ]

