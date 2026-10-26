from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('datasync', '0005_bulk_round_sync')]

    operations = [
        migrations.AddField(
            model_name='bulksyncrun', name='categories',
            field=models.JSONField(blank=True, default=list, verbose_name='Selected categories'),
        ),
        migrations.AlterField(
            model_name='bulksyncrun', name='category',
            field=models.CharField(max_length=100, choices=[
                ('all', 'All categories'), ('mscc.round', 'Round'),
                ('locations.center', 'Centres (including partners)'),
                ('mscc.teacher', 'Teachers'),
                ('mscc.registration', 'Registrations (including children and photos)'),
                ('mscc.education_service', 'Education services'),
                ('mscc.education_assessment', 'Education assessments'),
                ('mscc.education_grading', 'Education grading'),
                ('mscc.referral', 'Referrals'),
                ('attendances.mscc_attendance', 'Attendance (including child rows)'),
                ('selected', 'Selected categories'),
            ]),
        ),
    ]
