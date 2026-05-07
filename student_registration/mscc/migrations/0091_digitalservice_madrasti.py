from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0090_alter_educationservice_education_program'),
    ]

    operations = [
        migrations.AddField(
            model_name='digitalservice',
            name='madrasti',
            field=models.CharField(blank=True, choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')], max_length=100, null=True, verbose_name='Madrasti'),
        ),
    ]
