from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0166_alter_school_active_during_emergency'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicSchool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('cerd', models.PositiveIntegerField(
                    unique=True,
                    validators=[MinValueValidator(0), MaxValueValidator(999999)],
                    verbose_name='CERD number',
                )),
            ],
            options={
                'verbose_name': 'Public school',
                'verbose_name_plural': 'Public schools',
                'ordering': ['name'],
            },
        ),
    ]
