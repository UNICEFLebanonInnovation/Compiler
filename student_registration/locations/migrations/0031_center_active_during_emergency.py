from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0030_programstaff_is_active_current_round'),
    ]

    operations = [
        migrations.AddField(
            model_name='center',
            name='active_during_emergency',
            field=models.CharField(
                blank=True,
                choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')],
                max_length=50,
                null=True,
                verbose_name='Active during emergency',
            ),
        ),
    ]
