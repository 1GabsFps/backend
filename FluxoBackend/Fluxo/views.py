from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import mercadopago
from .models import Cartao, User, get_uuid
from validate_docbr import CPF
import jwt
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import logging

sdk = mercadopago.SDK(
    "TEST-5462818721115165-090312-c154f5048e76cc504e0d051206edb322-236803241"
)


class CadastroView(APIView):
    def post(self, request):
        # Validação do CPF
        cpf = request.data.get("cpf")
        if not CPF().validate(cpf):
            return Response(
                {"error": "Invalid CPF"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Criação do usuário
        user_data = {
            "username": request.data.get("name"),
            "password": request.data.get("password"),
            "cpf": cpf,
            "email": request.data.get("email"),
        }
        user = User.objects.create(**user_data)
        user.save()
        return Response({"user": user.id}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        cpf = request.data.get("cpf")
        password = request.data.get("password")
        user = get_object_or_404(User, cpf=cpf, password=password)
        # Generate JWT token
        payload = {
            "user_id": user.id,
            "username": user.username,
            "password": user.password,
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return Response({"token": token}, status=status.HTTP_200_OK)


class PagamentoView(APIView):

    def post(request):
        if request.method == "POST":
            payment_data = {
                "transaction_amount": float(request.POST.get("transaction_amount")),
                "token": request.POST.get("token"),
                "description": request.POST.get("description"),
                "installments": int(request.POST.get("installments")),
                "payment_method_id": request.POST.get("payment_method_id"),
                "payer": {"email": request.POST.get("email")},
            }

            payment_response = sdk.payment().create(payment_data)
            payment = payment_response["response"]

            if payment.get("status") == "approved":
                # Adicionar o valor da transação ao saldo do cartão
                User = User.objects.get(id=request.POST.get("user_id"))
                Cartao = Cartao.objects.get(id_Proprietario=User)
                Cartao.saldo += payment.get("transaction_amount")
                Cartao.save()

            return JsonResponse(payment)
        else:
            return JsonResponse({"error": "Invalid request method"}, status=400)


class AtribuirCartao(APIView):
    def post(self, request):
        token = request.get("Token")
        token_decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = token_decoded.get("user_id")
        cpf = User.objects.get(id=user_id).cpf
        classe = request.data.get("classe")
        user = get_object_or_404(User, cpf=cpf)

        # Tentativa de leitura do UUID do cartão a partir do leitor NFC
        try:
            uuid = get_uuid()
            if not uuid:
                return Response(
                    {"error": "Falha ao ler o UUID do cartão"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except Exception as e:
            return Response(
                {"error": f"Erro ao conectar com o leitor NFC: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        card = Cartao.objects.create(
            id_Proprietario=user, saldo=0, uuid=uuid, classe=classe
        )
        return Response(
            {"message": "Cartão atribuído com sucesso", "card_id": card.id},
            status=status.HTTP_201_CREATED,
        )


class PassarCartao(APIView):
    def get(self, request, *args, **kwargs):
        try:
            uuid = get_uuid()
            if not uuid:
                return Response(
                    {"error": "Falha ao ler o UUID do cartão"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            cartao = get_object_or_404(Cartao, uuid=uuid)
            classe_cartao = cartao.classe
            match classe_cartao:
                case "Normal":
                    if cartao.saldo >= 4.4:
                        cartao.saldo -= 4.4
                        cartao.save()
                        return Response(
                            {
                                "message": "Passagem realizada com sucesso",
                                "saldo": cartao.saldo,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {"error": "Saldo insuficiente"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                case "Estudante":
                    if cartao.saldo >= 2.2:
                        cartao.saldo -= 2.2
                        cartao.save()
                        return Response(
                            {
                                "message": "Passagem realizada com sucesso",
                                "saldo": cartao.saldo,
                            },
                            status=status.HTTP_200_OK,
                        )
                    else:
                        return Response(
                            {"error": "Saldo insuficiente"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                case "Especial":
                    return Response(
                        {
                            "message": "Passagem realizada com sucesso",
                            "saldo": cartao.saldo,
                        },
                        status=status.HTTP_200_OK,
                    )
                case "Idoso":
                    return Response(
                        {
                            "message": "Passagem realizada com sucesso",
                            "saldo": cartao.saldo,
                        },
                        status=status.HTTP_200_OK,
                    )

        except Exception as e:
            return Response(
                {"error": f"Erro ao processar a requisição: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PegarUser(APIView):
    def post(self, request):
        token = request.data.get("token")
        tokenBytes = token.encode("utf-8")
        token_decoded = jwt.decode(
            tokenBytes, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id = token_decoded.get("user_id")
        user = get_object_or_404(User, id=user_id)
        return Response(
            {"user": user.username, "cpf": user.cpf, "email": user.email},
            status=status.HTTP_200_OK,
        )


class PegarCartao(APIView):
    def post(self, request):
        token = request.data.get("token")
        tokenBytes = token.encode("utf-8")
        token_decoded = jwt.decode(
            tokenBytes, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id = token_decoded.get("user_id")
        user = get_object_or_404(User, id=user_id)
        cartoes = Cartao.objects.filter(id_Proprietario=user)

        if not cartoes.exists():
            return Response(
                {"error": "No cards found for this user"},
                status=status.HTTP_404_NOT_FOUND,
            )

        cartoes_data = {}
        for cartao in cartoes:
            cartaonum = f"cartao{cartao.id}"
            cartoes_data[cartaonum] = {
                "id": cartao.id,
                "saldo": cartao.saldo,
                "classe": cartao.classe,
            }

        return Response(cartoes_data, status=status.HTTP_200_OK)


# Configuração do logger
logger = logging.getLogger(__name__)


class RecarregarCartao(APIView):
    def post(self, request):

        transaction_amount = request.data.get("transaction_amount")
        email = request.data.get("email")

        if not transaction_amount or not email:
            return Response(
                {"error": "transaction_amount and email are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            transaction_amount = float(transaction_amount)
        except ValueError:
            return Response(
                {"error": "transaction_amount must be a valid number"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        preference_data = {
            "items": [
                {
                    "title": "Recarga de Cartão",
                    "quantity": 1,
                    "unit_price": transaction_amount,
                }
            ],
            "payer": {
                "email": email,
            },
            "back_urls": {
                "success": "http://www.seusite.com/success",
                "failure": "http://www.seusite.com/failure",
                "pending": "http://www.seusite.com/pending",
            },
            "auto_return": "approved",
            "notification_url": "https://1cea-2804-431-cfeb-fed-806f-de33-8ea4-7f7d.ngrok-free.app/notifications/",
        }

        try:
            preference_response = sdk.preference().create(preference_data)
            logger.debug(f"Preference response: {preference_response}")

            if preference_response.get("status") != 201:
                logger.error(
                    f"Failed to create payment preference: {preference_response}"
                )
                return Response(
                    {
                        "error": f"Failed to create payment preference: {preference_response}"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            preference = preference_response.get("response", {})
            init_point = preference.get("init_point")
            if not init_point:
                logger.error(f"init_point not found in response: {preference_response}")
                return Response(
                    {
                        "error": f"init_point not found in response: {preference_response}"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return JsonResponse({"init_point": init_point}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("An error occurred while creating payment preference")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RecarregarCartao(APIView):
    def post(self, request):

        transaction_amount = request.data.get("transaction_amount")
        email = request.data.get("email")
        cartao = request.data.get("card_id")
        token = request.data.get("token")
        tokenBytes = token.encode("utf-8")
        token_decoded = jwt.decode(
            tokenBytes, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id = token_decoded.get("user_id")

        if not transaction_amount or not email:
            return Response(
                {"error": "transaction_amount and email are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            transaction_amount = float(transaction_amount)
        except ValueError:
            return Response(
                {"error": "transaction_amount must be a valid number"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        preference_data = {
            "items": [
                {
                    "title": "Recarga de Cartão",
                    "quantity": 1,
                    "unit_price": transaction_amount,
                }
            ],
            "payer": {
                "email": email,
            },
            "back_urls": {
                "success": "http://localhost:3000/cartoes",
                "failure": "http://www.seusite.com/failure",
                "pending": "http://www.seusite.com/pending",
            },
            "auto_return": "approved",
            "notification_url": "https://6b11-2804-431-cfeb-fed-806f-de33-8ea4-7f7d.ngrok-free.app/notifications/",
            "external_reference": f"{user_id}-{cartao}",
        }

        try:
            preference_response = sdk.preference().create(preference_data)
            logger.debug(f"Preference response: {preference_response}")

            preference = preference_response.get("response", {})
            init_point = preference.get("init_point")
            if not init_point:
                logger.error(f"init_point not found in response: {preference_response}")
                return Response(
                    {"error": "init_point not found in response"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return JsonResponse({"init_point": init_point}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("An error occurred while creating payment preference")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@csrf_exempt
def payment_notification(request):
    if request.method == "POST":
        data = request.GET.dict()  # Use request.GET para obter os parâmetros da URL
        topic = data.get("type")  # O campo correto é "type" e não "topic"
        if topic != "payment":
            logger.error("Invalid topic")
            return JsonResponse({"error": "Invalid topic"}, status=400)

        payment_id = data.get("data.id")
        if not payment_id:
            logger.error("Payment ID not found")
            return JsonResponse({"error": "Payment ID not found"}, status=400)

        try:
            payment_response = sdk.payment().get(payment_id)
            payment = payment_response.get("response")
            if not payment:
                logger.error("Failed to retrieve payment information")
                return JsonResponse(
                    {"error": "Failed to retrieve payment information"}, status=400
                )

            if payment.get("status") != "approved":
                logger.error("Payment not approved")
                return JsonResponse({"error": "Payment not approved"}, status=400)

            external_reference = payment.get("external_reference")
            if not external_reference:
                logger.error("External reference not found in payment")
                return JsonResponse(
                    {"error": "External reference not found in payment"}, status=400
                )

            user_id, cartao_id = external_reference.split("-")
            user = User.objects.get(id=user_id)
            cartao = Cartao.objects.get(id=cartao_id, id_Proprietario=user)
            cartao.saldo += payment.get("transaction_amount")
            cartao.save()

            logger.info("Payment processed successfully")
            return JsonResponse(
                {"message": "Payment processed successfully"}, status=200
            )
        except Exception as e:
            logger.exception("An error occurred while processing payment notification")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        logger.error("Invalid request method")
        return JsonResponse({"error": "Invalid request method"}, status=400)
