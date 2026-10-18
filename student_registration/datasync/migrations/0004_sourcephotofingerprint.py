from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('datasync', '0003_photo_resource')]
    operations = [migrations.CreateModel(
        name='SourcePhotoFingerprint',
        fields=[
            ('student_id', models.CharField(max_length=64, primary_key=True, serialize=False)),
            ('storage_name', models.TextField()),
            ('source_version', models.CharField(max_length=64)),
            ('sha256', models.CharField(max_length=64)),
            ('size', models.PositiveIntegerField()),
        ],
    )]
