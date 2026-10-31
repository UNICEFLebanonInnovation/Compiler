from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('child', '0020_child_unicef_id_new'),
    ]

    operations = [
        migrations.AddField(
            model_name='child',
            name='country_of_birth',
            field=models.CharField(
                blank=True, null=True, max_length=50,
                choices=[('', 'Select an option'), ('Lebanon', 'Lebanon'),
                         ('Syria', 'Syria'), ('Other', 'Other')],
                verbose_name='Country of Birth',
            ),
        ),
        migrations.AddField(
            model_name='child',
            name='place_of_birth',
            field=models.CharField(
                blank=True, null=True, max_length=255,
                verbose_name='Place of Birth',
                help_text='Place of birth similar in the Official ID',
            ),
        ),
    ]
