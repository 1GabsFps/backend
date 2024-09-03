from django.shortcuts import render
from django.http import JsonResponse
import mercadopago
from rest_framework import viewsets
from .models import Cartao

# Configurar o SDK do Mercado Pago
sdk = mercadopago.SDK("YOUR_ACCESS_TOKEN")

class CadastroView(viewsets.ModelViewSet):
    pass

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
                cartao = Cartao.objects.get(id=request.POST.get('cartao_id'))
                cartao.saldo += payment.get('transaction_amount')
                cartao.save()

            return JsonResponse(payment)
        else:
            return JsonResponse({"error": "Invalid request method"}, status=400)