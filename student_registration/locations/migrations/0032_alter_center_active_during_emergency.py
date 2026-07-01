from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0031_center_active_during_emergency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='center',
            name='active_during_emergency',
            field=models.CharField(
                blank=True,
                choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')],
                max_length=50,
                null=True,
                verbose_name='Active in emergency?',
            ),
        ),
    ]
