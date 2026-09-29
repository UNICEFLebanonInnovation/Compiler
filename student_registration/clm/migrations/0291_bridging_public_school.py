from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0290_bridging_profile_picture'),
        ('schools', '0167_publicschool'),
    ]

    operations = [
        migrations.AddField(
            model_name='bridging',
            name='public_school',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='bridging_referrals',
                to='schools.publicschool',
                verbose_name='Public school',
            ),
        ),
    ]
