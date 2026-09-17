from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0033_alter_center_type'),
        ('mscc', '0099_remove_legoservice_lego_play_and_learn_activities'),
        ('schools', '0166_alter_school_active_during_emergency'),
    ]

    operations = [
        migrations.AddField(
            model_name='referral', name='formal_education_school',
            field=models.TextField(blank=True, null=True, verbose_name='Formal Education School'),
        ),
        migrations.AddField(
            model_name='referral', name='formal_education_school_type',
            field=models.CharField(blank=True, choices=[('', '----------'), ('Public', 'Public'), ('Private', 'Private'), ('Semi-Private', 'Semi-Private')], max_length=100, null=True, verbose_name='School Type'),
        ),
        migrations.AddField(
            model_name='referral', name='cerd_number',
            field=models.CharField(blank=True, max_length=6, null=True, verbose_name='CERD#'),
        ),
        migrations.AddField(
            model_name='referral', name='formal_education_grade_level',
            field=models.CharField(blank=True, choices=[('', '----------'), ('grade_one', 'Grade 1'), ('grade_two', 'Grade 2'), ('grade_three', 'Grade 3'), ('grade_four', 'Grade 4'), ('grade_five', 'Grade 5'), ('grade_six', 'Grade 6'), ('grade_seven', 'Grade 7'), ('grade_eight', 'Grade 8'), ('grade_nine', 'Grade 9'), ('grade_ten', 'Grade 10'), ('grade_eleven', 'Grade 11'), ('grade_twelve', 'Grade 12')], max_length=12, null=True, verbose_name='Grade level the Child is enrolled in'),
        ),
        migrations.AddField(model_name='referral', name='transition_arabic_grade', field=models.PositiveSmallIntegerField(blank=True, null=True)),
        migrations.AddField(model_name='referral', name='transition_foreign_languages_grade', field=models.PositiveSmallIntegerField(blank=True, null=True)),
        migrations.AddField(model_name='referral', name='transition_math_grade', field=models.PositiveSmallIntegerField(blank=True, null=True)),
        migrations.AddField(
            model_name='referral', name='retention_support_enrolled',
            field=models.CharField(blank=True, choices=[('', '----------'), ('Yes', 'Yes'), ('No', 'No')], max_length=3, null=True, verbose_name='Was the child referred and enrolled in a Retention Support programme?'),
        ),
        migrations.AddField(
            model_name='referral', name='retention_support_partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='schools.partnerorganization', verbose_name='Which partner?'),
        ),
        migrations.AddField(
            model_name='referral', name='retention_support_center',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='locations.center', verbose_name='Which center?'),
        ),
    ]
