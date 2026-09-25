from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0288_bridging_referral_school'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bridging',
            name='cerd_number',
        ),
        migrations.RemoveField(
            model_name='bridging',
            name='referral_school',
        ),
        migrations.RemoveField(
            model_name='bridging',
            name='referral_school_type',
        ),
    ]
