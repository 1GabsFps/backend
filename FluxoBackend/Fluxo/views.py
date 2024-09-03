from django.shortcuts import render
from django.http import JsonResponse
import mercadopago
from rest_framework import viewsets
from .models import Cartao, User
from cpf import validate_cpf

# Configurar o SDK do Mercado Pago
sdk = mercadopago.SDK("YOUR_ACCESS_TOKEN")

class CadastroView(viewsets.ModelViewSet):
    def create_user(request):
        if request.method == 'POST':
            user_data = {
                "name": request.POST.get('name'),
                "email": request.POST.get('email'),
                "Cpf": request.POST.get('Cpf'),
                "senha": request.POST.get('senha')
            }
            
            if not validate_cpf(user_data['Cpf']):
                return JsonResponse({"error": "Invalid CPF"}, status=400)
            
            if User.objects.filter(email=user_data['email']).exists():
                return JsonResponse({"error": "User already exists"}, status=400)
            elif User.objects.filter(Cpf=user_data['Cpf']).exists():
                return JsonResponse({"error": "User already exists"}, status=400)
            else:
                User.objects.create(**user_data)
                return JsonResponse({"success": "User created successfully"})
            

class PagamentoView(viewsets.ModelViewSet):
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
        
class AtribuirCartao(viewsets.ModelViewSet):
    def assign_card(request):
        if request.method == 'POST':
            