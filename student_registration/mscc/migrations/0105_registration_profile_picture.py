from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('mscc', '0104_serviceprogramoption_is_tls')]
    operations = [
        migrations.AddField(
            model_name='registration',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True,
                                    upload_to='mscc/profile_pictures/',
                                    verbose_name='Profile Picture'),
        ),
    ]
