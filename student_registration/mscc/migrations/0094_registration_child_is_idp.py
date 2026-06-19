from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0093_educationprogrammeassessment_mid_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='child_is_idp',
            field=models.CharField(blank=True, choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')], max_length=10, null=True, verbose_name='Child is IDP?'),
        ),
    ]
