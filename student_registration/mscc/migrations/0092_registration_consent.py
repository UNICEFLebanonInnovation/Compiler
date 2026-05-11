from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0091_digitalservice_madrasti'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='consent',
            field=models.CharField(blank=True, choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')], max_length=10, null=True, verbose_name='Informed Consent Received to Share Data Externally'),
        ),
    ]
