from django.db import migrations, models


def copy_youth_assessments(apps, schema_editor):
    assessment_model = apps.get_model('mscc', 'EducationProgrammeAssessment')
    youth_assessments = assessment_model.objects.filter(programme_type__startswith='Y')

    for assessment in youth_assessments.iterator():
        assessment.youth_pre_test = assessment.pre_test
        assessment.youth_post_test = assessment.post_test
        assessment.save(update_fields=['youth_pre_test', 'youth_post_test'])


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
        migrations.RunPython(copy_youth_assessments, migrations.RunPython.noop),
    ]
