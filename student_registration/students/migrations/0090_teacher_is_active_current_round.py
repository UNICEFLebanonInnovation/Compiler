from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0089_student_unicef_id_backup_student_unicef_id_new_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacher',
            name='is_active_current_round',
            field=models.CharField(
                blank=True,
                choices=[('', '----------'), ('yes', 'Yes'), ('no', 'No')],
                max_length=10,
                null=True,
                verbose_name='The staff still active in current round?'
            ),
        ),
    ]
