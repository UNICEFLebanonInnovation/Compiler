from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0098_educationprogrammeassessment_youth_tests'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='legoservice',
            name='lego_play_and_learn_activities',
        ),
    ]
