from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0027_alter_activityinfolocation_level_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='center',
            name='is_tarl',
            field=models.CharField(blank=True, choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')], max_length=50, null=True, verbose_name='Is the center a TARL center?'),
        ),
    ]
