from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.CadastroView.as_view(), name='cadastro'),
]