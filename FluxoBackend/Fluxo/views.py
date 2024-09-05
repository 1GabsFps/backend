from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.http import JsonResponse
import mercadopago
from .models import Cartao, User
from validate_docbr import CPF
from django.contrib.auth.models import User

sdk = mercadopago.SDK("YOUR_ACCESS_TOKEN")

class CadastroView(APIView):
    def post(self, request):
        # Validação do CPF
        cpf = request.data.get('cpf')
        if not CPF().validate(cpf):
            return Response({"error": "Invalid CPF"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Criação do usuário
        user_data = {
            "username": request.data.get('name'),
            "password": request.data.get('password'),
            "email": request.data.get('email')
        }
        user = User.objects.create_user(**user_data)
        
        return Response({"user": user.id}, status=status.HTTP_201_CREATED)

class PagamentoView(APIView):
    def create_payment(request):
        if request.method == 'POST':
            payment_data = {
                "transaction_amount": float(request.POST.get('transaction_amount')),
                "token": request.POST.get('token'),
                "description": request.POST.get('description'),
                "installments": int(request.POST.get('installments')),
                "payment_method_id": request.POST.get('payment_method_id'),
                "payer": {
                    "email": request.POST.get('email')
                }
            }

            payment_response = sdk.payment().create(payment_data)
            payment = payment_response["response"]

            if payment.get('status') == 'approved':
                # Adicionar o valor da transação ao saldo do cartão
                User = User.objects.get(id=request.POST.get('user_id'))
                Cartao = Cartao.objects.get(id_Proprietario=User)
                Cartao.saldo += payment.get('transaction_amount')
                Cartao.save()

            return JsonResponse(payment)
        else:
            return JsonResponse({"error": "Invalid request method"}, status=400)
        
class AtribuirCartao(APIView):
    def assign_card(request):
        if request.method == 'POST':
            pass