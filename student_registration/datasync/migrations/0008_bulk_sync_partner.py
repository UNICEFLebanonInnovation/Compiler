import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('datasync', '0007_bulk_sync_global_records'), ('schools', '0001_initial')]

    operations = [migrations.AddField(
        model_name='bulksyncrun', name='partner',
        field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT,
                                to='schools.partnerorganization', verbose_name='Partner'),
    )]
