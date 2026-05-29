from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendances', '0067_clmattendance_section'),
    ]

    operations = [
        migrations.AlterField(
            model_name='msccattendancechild',
            name='absence_reason_other',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='specify'),
        ),
    ]
