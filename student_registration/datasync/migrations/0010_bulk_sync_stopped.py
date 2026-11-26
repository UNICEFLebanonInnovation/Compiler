from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('datasync', '0009_alter_bulksyncrun_category_alter_syncevent_resource')]
    operations = [migrations.AlterField(model_name='bulksyncrun', name='preparation',
        field=models.CharField(max_length=12, default='waiting', choices=[
            ('waiting', 'Starting'), ('ready', 'Syncing'), ('failed', 'Could not start'), ('cancelled', 'Stopped')]))]
