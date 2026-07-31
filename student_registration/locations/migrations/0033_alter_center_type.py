from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0032_center_is_tls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='center',
            name='type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Municipality', 'Municipality'),
                    ('Collective Settlement', 'Collective Settlement'),
                    ('Informal Settlement', 'Informal Settlement'),
                    ('Welfare Center', 'Welfare Center'),
                    ('Community Hub', 'Community Hub'),
                    ('SDC', 'SDC'),
                ],
                max_length=100,
                null=True,
                verbose_name='Type',
            ),
        ),
    ]
