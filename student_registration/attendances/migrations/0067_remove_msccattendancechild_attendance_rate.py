from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendances', '0066_msccattendancechild_attendance_rate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='msccattendancechild',
            name='attendance_rate',
        ),
    ]
