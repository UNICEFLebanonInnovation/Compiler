from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0100_referral_transition_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referral',
            name='referred_formal_education',
        ),
    ]
