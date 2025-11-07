from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0084_serviceprogramoption'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationservice',
            name='ppl_sector',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', '----------'),
                    ('YAD', 'YAD'),
                    ('CP', 'CP'),
                    ('Health', 'Health'),
                    ('WASH', 'WASH'),
                    ('Nutrition', 'Nutrition'),
                ],
                max_length=50,
                null=True,
                verbose_name='PPL Sector',
            ),
        ),
    ]
