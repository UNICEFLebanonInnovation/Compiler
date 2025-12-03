from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mscc', '0085_educationservice_ppl_sector'),
    ]

    operations = [
        migrations.CreateModel(
            name='TarlAssessment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('pre_test', models.JSONField(default=dict)),
                ('post_test', models.JSONField(default=dict)),
                ('mid_test', models.JSONField(default=dict)),
                ('programme_type', models.CharField(blank=True, max_length=100, null=True, verbose_name='Education Programme Type')),
                ('registration', models.ForeignKey(blank=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='mscc.registration')),
            ],
            options={
                'ordering': ['id'],
                'verbose_name': 'TARL Assessment',
                'verbose_name_plural': 'TARL Assessments',
            },
        ),
    ]
