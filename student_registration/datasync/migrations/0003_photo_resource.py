"""Preserve legacy photo events for conversion into registration deliveries."""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('datasync', '0002_alter_syncevent_resource')]
    operations = [migrations.AlterField(
        model_name='syncevent', name='resource',
        field=models.CharField(max_length=100, choices=[
            ('child.photo', 'Child photo (multipart)'),
            ('mscc.round', 'Round'), ('locations.center', 'Center'),
            ('mscc.teacher', 'Teacher'), ('mscc.registration', 'Registration'),
            ('mscc.education_service', 'Child education situation'),
            ('mscc.education_assessment', 'Education assessment'),
            ('mscc.education_grading', 'Grading'), ('mscc.referral', 'Referral'),
            ('attendances.mscc_attendance', 'Attendance'), ('child.child', 'Child'),
        ], db_index=True,
                               verbose_name='Resource'),
    )]
