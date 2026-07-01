from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0165_educationallevel_name_en'),
    ]

    operations = [
        migrations.AlterField(
            model_name='school',
            name='active_during_emergency',
            field=models.CharField(
                blank=True,
                choices=[('', '----------'), ('yes', 'Yes'), ('no', 'No')],
                max_length=10,
                null=True,
                verbose_name='Active in emergency?',
            ),
        ),
    ]
