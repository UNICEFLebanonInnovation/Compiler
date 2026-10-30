from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clm', '0291_bridging_public_school'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bridging',
            name='learning_result',
            field=models.CharField(
                blank=True, null=True, max_length=100,
                choices=[
                    ('', '----------'),
                    ('graduated_to_Bridging_next_level', 'Progress to the next Dirasa level'),
                    ('graduated_to_Bridging_next_round_same_level', 'Repeat the same Dirasa level'),
                    ('dropout', 'Drop out'),
                    ('referred_public_school', 'Referred to formal education'),
                    ('referred_to_tvet', 'Referred to TVET'),
                    ('other', 'Referred to another pathway'),
                ],
                verbose_name='Learning result',
            ),
        ),
    ]
