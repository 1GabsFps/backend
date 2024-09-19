# Generated by Django 5.1 on 2024-09-05 11:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cartao',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('saldo', models.DecimalField(decimal_places=2, max_digits=10)),
                ('uuid', models.CharField(max_length=32)),
                ('valido', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Faq',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('pergunta', models.CharField(max_length=255)),
                ('resposta', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32)),
                ('Cpf', models.CharField(max_length=11)),
                ('email', models.EmailField(max_length=32)),
                ('senha', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='saldo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('id_cartao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saldo_cartao', to='Fluxo.cartao')),
            ],
        ),
        migrations.CreateModel(
            name='transacao',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('data', models.DateTimeField()),
                ('status', models.BooleanField(default=True)),
                ('id_cartao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transacao_cartao', to='Fluxo.cartao')),
            ],
        ),
        migrations.AddField(
            model_name='cartao',
            name='id_Proprietario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Fluxo.user'),
        ),
    ]