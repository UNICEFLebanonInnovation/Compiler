from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0101_remove_referral_referred_formal_education'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referral',
            name='cerd_number',
        ),
        migrations.RemoveField(
            model_name='referral',
            name='formal_education_school_type',
        ),
        migrations.RemoveField(
            model_name='referral',
            name='referred_school',
        ),
    ]
