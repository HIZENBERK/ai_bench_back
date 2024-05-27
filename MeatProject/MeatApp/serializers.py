from rest_framework import serializers
from .models import User, Order, Stock, Product

# class EmpInfoserializers(serializers.ModelSerializer):
#     class Meta:
#         model = EmpInfo
#         fields = '__all__'
#
# class LoginInfoserializers(serializers.ModelSerializer):
#     class Meta:
#         model = LoginInfo
#         fields = '__all__'



class Userserializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    EmpNo = serializers.CharField(max_length=10)
    password = serializers.CharField(write_only=True)


class Orderserializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class Stockserializers(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class Productserializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'