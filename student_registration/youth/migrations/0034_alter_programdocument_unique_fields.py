from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('youth', '0033_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programdocument',
            name='project_code',
            field=models.CharField(max_length=100, unique=True, verbose_name='Project Code'),
        ),
        migrations.AlterField(
            model_name='programdocument',
            name='project_name',
            field=models.CharField(max_length=250, unique=True, verbose_name='Project Name'),
        ),
    ]
