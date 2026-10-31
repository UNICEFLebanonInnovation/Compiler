from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='FiguresSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('programme', models.CharField(db_index=True, max_length=32)),
                ('year', models.CharField(help_text='the round or year the counts cover', max_length=32)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('seconds', models.FloatField(default=0, help_text='how long the counting took')),
                ('payload', models.JSONField()),
            ],
            options={
                'ordering': ('-created_at',),
                'indexes': [models.Index(fields=['programme', 'year', '-created_at'],
                                         name='figures_snapshot_lookup')],
            },
        ),
    ]
