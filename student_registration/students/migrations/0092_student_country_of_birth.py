from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0091_alter_teacher_registration_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='country_of_birth',
            field=models.CharField(
                blank=True, null=True, max_length=50,
                choices=[('', 'Select an option'), ('Lebanon', 'Lebanon'),
                         ('Syria', 'Syria'), ('Other', 'Other')],
                verbose_name='Country of Birth',
            ),
        ),
    ]
