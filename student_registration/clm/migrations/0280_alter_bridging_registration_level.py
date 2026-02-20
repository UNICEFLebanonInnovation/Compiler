from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0279_alter_abln_cadaster_alter_abln_center_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bridging',
            name='registration_level',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', '----------'),
                    ('level_one', 'Level one'),
                    ('level_two', 'Level two'),
                    ('level_three', 'Level three'),
                    ('grade_one', 'Grade one'),
                    ('grade_two', 'Grade two'),
                    ('grade_three', 'Grade three'),
                    ('grade_four', 'Grade four'),
                    ('grade_five', 'Grade five'),
                    ('grade_six', 'Grade six'),
                    ('grade_seven', 'Grade seven'),
                    ('grade_eight', 'Grade eight'),
                    ('grade_nine', 'Grade nine'),
                ],
                max_length=100,
                null=True,
                verbose_name='Registration level'
            ),
        ),
    ]
