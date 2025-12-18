from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0088_registration_attendance_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='total_absence',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='registration',
            name='total_attendance',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
