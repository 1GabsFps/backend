from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.CadastroView.as_view(), name='cadastro'),
    path('atribuir_cartao/', views.AtribuirCartao.as_view() ,  name='atribuir_cartao'),
    path('passar_cartao/', views.PassarCartao.as_view(), name='passar_cartao'),
    path("login/", views.LoginView.as_view(), name="login"),
    path("getuser/" , views.PegarUser.as_view(), name="getuser"),
    path("cartoes/", views.PegarCartao.as_view(), name="cartoes"),
]