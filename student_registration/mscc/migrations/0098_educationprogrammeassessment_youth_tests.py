from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0097_alter_educationservice_education_program_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationprogrammeassessment',
            name='youth_pre_test',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='educationprogrammeassessment',
            name='youth_post_test',
            field=models.JSONField(default=dict),
        ), 
    ]
