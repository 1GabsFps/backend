# Generated by Django 5.1.1 on 2024-09-05 17:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Fluxo', '0002_remove_user_cpf_remove_user_senha_user_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='created_at',
        ),
    ]