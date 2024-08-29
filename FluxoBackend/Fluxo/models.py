from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)
    Cpf = models.CharField(max_length=11)
    email = models.EmailField(max_length=32)
    senha = models.CharField(max_length=32).encode('utf-8')
    

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
    

class saldo(models.Model):
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    id_cartao = models.ForeignKey(Cartao, on_delete=models.CASCADE)
    
class transacao(models.Model):
    id = models.AutoField(primary_key=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField()
    id_cartao = models.ForeignKey(Cartao, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)