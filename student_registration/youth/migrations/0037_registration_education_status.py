# Generated manually on 2026-06-10

from django.db import migrations, models


EDUCATION_STATUS_CHOICES = [
    ('', '----------'),
    ('Never registered in any formal school before', 'Never registered in any formal school before'),
    ("Was registered in formal school but didn't continue", "Was registered in formal school but didn't continue"),
    ('Was registered in non formal program and was referred to MSCC', 'Was registered in non formal program and was referred to MSCC'),
    ("Was registered in non formal program but didn't continue", "Was registered in non formal program but didn't continue"),
    ('Was enrolled in TVET Programs', 'Was enrolled in TVET Programs'),
    ('Was Registered in Formal Education but not attending', 'Was Registered in Formal Education but not attending'),
    ('Currently registered in Formal Education school', 'Currently registered in Formal Education school'),
    ('Currently registered in Formal Education school but not attending', 'Currently registered in Formal Education school but not attending'),
    ('Completed university degree', 'Completed university degree'),
    ('No', 'No'),
]


class Migration(migrations.Migration):

    dependencies = [
        ('youth', '0036_alter_programdocument_project_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='education_status',
            field=models.CharField(
                blank=True,
                choices=EDUCATION_STATUS_CHOICES,
                max_length=200,
                null=True,
                verbose_name="Youth's educational level when registering",
            ),
        ),
    ]
