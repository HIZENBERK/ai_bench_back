from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Order, Stock, Product, Client

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, User):
        token = super().get_token(User)
        # Frontend에서 더 필요한 정보가 있다면 여기에 추가적으로 작성하면 됩니다. token["is_superuser"] = user.is_superuser 이런식으로요.
        token['username'] = User.username
        token['Position'] = User.Position
        token['Job'] = User.Job
        return token


class Userserializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class SingupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=10)
    Position = serializers.CharField(max_length=5)
    Job = serializers.CharField(max_length=5)
    # class Meta:
    #     model = User
    #     fields = ('username', 'Position', 'Job')

    # def create(self, validated_data):
    #     user = User.objects.create(
    #         username=validated_data['username']
    #     )
    #     user.set_password(user.generate_password())
    #     user.save()

class LoginSerializer(serializers.Serializer):
    empNo = serializers.CharField(max_length=10)
    password = serializers.CharField(max_length=128, write_only=True)


class OrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class StockSerializers(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class ProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ClientSerializers(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'