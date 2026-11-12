from django.db import migrations, models
from django.db.models import OuterRef, Subquery
import django.db.models.deletion


def populate_partners(apps, schema_editor):
    Registration = apps.get_model('youth', 'Registration')
    EnrolledPrograms = apps.get_model('youth', 'EnrolledPrograms')
    alias = schema_editor.connection.alias
    registration_partner = Registration.objects.using(alias).filter(
        pk=OuterRef('registration_id')
    ).values('partner_id')[:1]
    EnrolledPrograms.objects.using(alias).update(partner_id=Subquery(registration_partner))


class Migration(migrations.Migration):
    dependencies = [
        ('schools', '0159_alter_alpassignmentmatrix_level_and_more'),
        ('youth', '0038_registration_dropout_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrolledprograms',
            name='partner',
            field=models.ForeignKey(
                blank=True, null=True, related_name='+',
                on_delete=django.db.models.deletion.SET_NULL,
                to='schools.partnerorganization',
            ),
        ),
        migrations.RunPython(populate_partners, migrations.RunPython.noop),
    ]
