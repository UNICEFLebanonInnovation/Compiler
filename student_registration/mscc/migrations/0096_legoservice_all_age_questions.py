from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0095_serviceprogramoption_is_tarl'),
    ]

    operations = [
        migrations.AddField(
            model_name='legoservice',
            name='lego_play_and_learn_activities',
            field=models.CharField(
                blank=True,
                choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')],
                max_length=100,
                null=True,
                verbose_name='LEGO play & learn activities?',
            ),
        ),
        migrations.AddField(
            model_name='legoservice',
            name='participating_lego_events',
            field=models.CharField(
                blank=True,
                choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')],
                max_length=100,
                null=True,
                verbose_name='Is the child participating in LEGO events?',
            ),
        ),
    ]
