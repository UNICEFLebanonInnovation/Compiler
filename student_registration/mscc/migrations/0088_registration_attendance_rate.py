from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0087_serviceprogramoption_is_education_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='attendance_rate',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
