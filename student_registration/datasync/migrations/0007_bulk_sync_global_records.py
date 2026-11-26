import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('datasync', '0006_bulk_sync_categories')]

    operations = [
        migrations.AlterField(
            model_name='bulksyncrun', name='round',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='mscc.round'),
        ),
        migrations.AlterModelOptions(
            name='bulksyncrun', options={
                'ordering': ['-created'], 'verbose_name': 'Bulk sync', 'verbose_name_plural': 'Bulk sync',
            },
        ),
    ]
