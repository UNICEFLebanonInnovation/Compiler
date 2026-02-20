from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0029_center_provide_french_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='programstaff',
            name='is_active_current_round',
            field=models.CharField(
                blank=True,
                choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')],
                max_length=50,
                null=True,
                verbose_name='The staff still active in current round?'
            ),
        ),
    ]
