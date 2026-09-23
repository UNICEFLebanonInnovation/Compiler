from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0287_bridging_public_school_referral_details'),
        ('schools', '0166_alter_school_active_during_emergency'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "UPDATE clm_bridging SET referral_school = NULL "
                "WHERE BTRIM(referral_school) = ''"
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='bridging',
            name='referral_school',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='schools.school',
                verbose_name='Formal Education school',
            ),
        ),
    ]
