from rest_framework import serializers

from .models import Web3User


class Web3UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = Web3User
    fields = '__all__'

