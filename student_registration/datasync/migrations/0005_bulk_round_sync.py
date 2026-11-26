import uuid

import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('datasync', '0004_sourcephotofingerprint'),
        ('mscc', '0095_serviceprogramoption_is_tarl'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BulkSyncRun',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('category', models.CharField(max_length=100, choices=[
                    ('all', 'All categories'), ('mscc.round', 'Round'),
                    ('locations.center', 'Centres (including partners)'),
                    ('mscc.teacher', 'Teachers'),
                    ('mscc.registration', 'Registrations (including children and photos)'),
                    ('mscc.education_service', 'Education services'),
                    ('mscc.education_assessment', 'Education assessments'),
                    ('mscc.education_grading', 'Education grading'),
                    ('mscc.referral', 'Referrals'),
                    ('attendances.mscc_attendance', 'Attendance (including child rows)'),
                ])),
                ('preparation', models.CharField(max_length=12, default='waiting', choices=[
                    ('waiting', 'Waiting to queue'), ('ready', 'Queued'), ('failed', 'Queueing failed'),
                ])),
                ('queued_counts', models.JSONField(default=dict)),
                ('last_error', models.TextField(blank=True)),
                ('requested_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mscc.round')),
            ],
            options={'ordering': ['-created'], 'verbose_name': 'Bulk sync by round', 'verbose_name_plural': 'Bulk sync by round'},
        ),
        migrations.AddField(
            model_name='syncevent', name='bulk_run',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                    related_name='events', to='datasync.bulksyncrun', verbose_name='Bulk sync run'),
        ),
    ]
