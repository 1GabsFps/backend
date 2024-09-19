# Generated by Django 5.1.1 on 2024-09-10 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Fluxo', '0005_remove_user_created_at_remove_user_groups_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartao',
            name='saldo',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='saldo',
            name='valor',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='transacao',
            name='valor',
            field=models.FloatField(default=0),
        ),
    ]