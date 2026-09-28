from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0289_remove_bridging_referral_school_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='bridging',
            name='profile_picture',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='uploads/bridging/profile_pictures',
                verbose_name='Profile Picture',
            ),
        ),
    ]
