from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0092_registration_consent'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationprogrammeassessment',
            name='mid_test',
            field=models.JSONField(default=dict),
        ),
    ]
