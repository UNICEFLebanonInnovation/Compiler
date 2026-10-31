from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('mscc', '0106_tls_summer_rs_programs')]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='photo_sync_cleared',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
