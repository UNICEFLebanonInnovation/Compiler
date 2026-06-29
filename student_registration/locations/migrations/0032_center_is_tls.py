from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0031_center_active_during_emergency'),
    ]

    operations = [
        migrations.AddField(
            model_name='center',
            name='is_tls',
            field=models.CharField(
                blank=True,
                choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')],
                max_length=50,
                null=True,
                verbose_name='Is TLS?',
            ),
        ),
    ]
