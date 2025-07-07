from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('backends', '0011_exportrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='exportrequest',
            name='selected_fields',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='exportrequest',
            name='file_format',
            field=models.CharField(default='csv', max_length=10),
        ),
    ]
