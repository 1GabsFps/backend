from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'cpf', 'senha']
        extra_kwargs = {
            'senha': {'write_only': True}
        }
        