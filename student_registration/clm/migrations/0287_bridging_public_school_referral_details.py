from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0286_bridging_term_assessments'),
        ('schools', '0166_alter_school_active_during_emergency'),
    ]

    operations = [
        migrations.AddField(model_name='bridging', name='cerd_number', field=models.CharField(blank=True, max_length=6, null=True, verbose_name='CERD#')),
        migrations.AddField(model_name='bridging', name='formal_education_grade_level', field=models.CharField(blank=True, choices=[('', '----------'), ('grade_five', 'Grade five'), ('grade_six', 'Grade six'), ('grade_seven', 'Grade seven'), ('grade_eight', 'Grade eight'), ('grade_nine', 'Grade nine'), ('grade_ten', 'Grade ten'), ('grade_eleven', 'Grade eleven'), ('grade_twelve', 'Grade twelve')], max_length=12, null=True, verbose_name='Grade level the Child is enrolled in')),
        migrations.AddField(model_name='bridging', name='transition_arabic_grade', field=models.PositiveSmallIntegerField(blank=True, null=True)),
        migrations.AddField(model_name='bridging', name='transition_foreign_languages_grade', field=models.PositiveSmallIntegerField(blank=True, null=True)),
        migrations.AddField(model_name='bridging', name='transition_math_grade', field=models.PositiveSmallIntegerField(blank=True, null=True)),
        migrations.AddField(model_name='bridging', name='retention_support_enrolled', field=models.CharField(blank=True, choices=[('', '----------'), ('yes', 'Yes'), ('no', 'No')], max_length=3, null=True, verbose_name='Was the child referred and enrolled in a Retention Support programme?')),
        migrations.AddField(model_name='bridging', name='retention_support_partner', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='schools.partnerorganization', verbose_name='Which partner?')),
        migrations.AddField(model_name='bridging', name='retention_support_center', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='clm.center', verbose_name='Which center?')),
    ]
