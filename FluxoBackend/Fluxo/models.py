from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from smartcard.Exceptions import NoCardException
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardConnectionException
import time


def get_uuid(max_retries=5, wait_time=2):
    for reader in readers():
        for attempt in range(max_retries):
            try:
                connection = reader.createConnection()
                connection.connect()
                atr = connection.getATR()
                cardrequest = CardRequest(timeout=10, readers=[reader])
                cardservice = cardrequest.waitforcard()
                cardservice.connection.connect()
                print(reader, atr)
                GET_UID = [
                    0xFF,
                    0xCA,
                    0x00,
                    0x00,
                    0x00,
                ]  # 0xFF significa que é um comando para o cartão, 0xCA é o comando para obter o UID, 0x00 é o byte P1, 0x00 é o byte P2 e 0x00 é o número de bytes a serem lidos do cartão

                response, sw1, _ = cardservice.connection.transmit(GET_UID)
                if sw1 == 0x90:
                    return toHexString(response)
                else:
                    return None
            except Exception as e:
                print(f"Tentativa {attempt + 1} falhou: {e}")
                time.sleep(wait_time)  # Espera antes de tentar novamente
    return None
class User(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150)
    email = models.EmailField(max_length=255, unique=True)
    cpf = models.CharField(max_length=11, unique=True)
    password = models.CharField(max_length=255)
class Cartao(models.Model):
    id = models.AutoField(primary_key=True)
    saldo = models.FloatField(default=0)
    uuid = models.CharField(max_length=32)
    id_Proprietario = models.ForeignKey(User, on_delete=models.CASCADE)
    valido = models.BooleanField(default=True)

class Faq(models.Model):
    id = models.AutoField(primary_key=True)
    pergunta = models.CharField(max_length=255)
    resposta = models.CharField(max_length=255)

class Saldo(models.Model):
    valor = models.FloatField(default=0)
    id_cartao = models.ForeignKey(Cartao, on_delete=models.CASCADE, related_name='saldo_cartao')

class Transacao(models.Model):
    id = models.AutoField(primary_key=True)
    valor = models.FloatField(default=0)
    data = models.DateTimeField()
    id_cartao = models.ForeignKey(Cartao, on_delete=models.CASCADE, related_name='transacao_cartao')
    status = models.BooleanField(default=True)
    
    