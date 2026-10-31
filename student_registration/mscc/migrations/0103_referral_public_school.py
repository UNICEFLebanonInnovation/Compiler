import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0102_remove_referral_school_details'),
        ('schools', '0167_publicschool'),
    ]

    operations = [
        migrations.AddField(
            model_name='referral',
            name='public_school',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='referrals',
                to='schools.publicschool',
                verbose_name='Public school',
            ),
        ),
    ]
