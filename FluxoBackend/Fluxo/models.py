from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, unique=True)
    cpf = models.CharField(max_length=11, unique=True)
    password = models.CharField(max_length=255)
class Cartao(models.Model):
    id = models.AutoField(primary_key=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    uuid = models.CharField(max_length=32)
    id_Proprietario = models.ForeignKey(User, on_delete=models.CASCADE)
    valido = models.BooleanField(default=True)

class Faq(models.Model):
    id = models.AutoField(primary_key=True)
    pergunta = models.CharField(max_length=255)
    resposta = models.CharField(max_length=255)

class Saldo(models.Model):
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    id_cartao = models.ForeignKey(Cartao, on_delete=models.CASCADE, related_name='saldo_cartao')

class Transacao(models.Model):
    id = models.AutoField(primary_key=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField()
    id_cartao = models.ForeignKey(Cartao, on_delete=models.CASCADE, related_name='transacao_cartao')
    status = models.BooleanField(default=True)