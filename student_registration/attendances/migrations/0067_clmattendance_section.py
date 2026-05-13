from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendances', '0066_alter_clmattendance_registration_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='clmattendance',
            name='section',
            field=models.CharField(blank=True, choices=[('', '----------'), ('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E'), ('f', 'F'), ('g', 'G'), ('h', 'H'), ('i', 'I'), ('j', 'J'), ('k', 'K'), ('l', 'L'), ('m', 'M'), ('n', 'N'), ('o', 'O'), ('p', 'P'), ('q', 'Q'), ('r', 'R'), ('s', 'S'), ('t', 'T'), ('u', 'U'), ('v', 'V'), ('w', 'W'), ('x', 'X'), ('y', 'Y'), ('z', 'Z')], max_length=1, null=True, verbose_name='Section'),
        ),
    ]
