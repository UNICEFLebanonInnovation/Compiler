from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0284_bridging_consent'),
    ]

    operations = [
        migrations.AddField(
            model_name='bridging',
            name='formal_education_referral_consent',
            field=models.FileField(blank=True, null=True, upload_to='uploads/student', verbose_name='Formal education referral consent'),
        ),
        migrations.AddField(
            model_name='bridging',
            name='other_additional_document',
            field=models.FileField(blank=True, null=True, upload_to='uploads/student', verbose_name='Other additional document'),
        ),
    ]
