from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0103_referral_public_school'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceprogramoption',
            name='is_tls',
            field=models.CharField(
                blank=True,
                choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')],
                max_length=100,
                null=True,
                verbose_name='TLS',
            ),
        ),
    ]
