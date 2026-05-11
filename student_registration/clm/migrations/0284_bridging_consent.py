from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0283_bridging_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='bridging',
            name='consent',
            field=models.CharField(blank=True, choices=[('', '----------'), ('yes', 'Yes'), ('no', 'No')], max_length=10, null=True, verbose_name='Informed Consent Received to Share Data Externally'),
        ),
    ]
