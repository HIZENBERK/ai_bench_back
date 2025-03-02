from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, Order, Stock, Product, Client, MeatPart, DeliveryAccident, Purchase, OtherCost

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

class LoginSerializer(serializers.Serializer):
    empNo = serializers.CharField(max_length=10)
    password = serializers.CharField(max_length=128, write_only=True)

class MeatPartSerializers(serializers.ModelSerializer):
    class Meta:
        model = MeatPart
        fields = '__all__'

class MeatPartInfoSerializers(serializers.ModelSerializer):
    class Meta:
        model = MeatPart
        fields = ['name', 'code']

# class OrderSerializers(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = '__all__'


class RegisterSerializers(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'

class RegisterDeleteSerializers(serializers.ModelSerializer):
    PurchaseNo = serializers.CharField(max_length=30)
    Method = serializers.CharField(max_length=10)

    class Meta:
        model = Purchase
        fields = ['PurchaseNo', 'Method']


class OrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['OrderNo', 'Part', 'OrderDate', 'OrderWorker', 'ETA', 'Client', 'OrderWeight', 'OrderPrice', 'OrderSituation']
        read_only_fields = ['OrderNo']

    def validate(self, data):
        # Add any custom validation logic here, if needed
        return data

class OrderUpdateSerializers(serializers.ModelSerializer):
    # OrderNo = serializers.CharField(max_length=255)
    class Meta:
        model = Order
        fields = ['OrderNo', 'Part', 'OrderDate', 'OrderWorker', 'ETA', 'Client', 'OrderWeight', 'OrderPrice', 'OrderSituation']
        read_only_fields = ['OrderNo']

class OrderInfoSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class StockSerializers(serializers.ModelSerializer):
    OrderNo = serializers.SlugRelatedField(queryset=Order.objects.all(), slug_field='OrderNo')
    class Meta:
        model = Stock
        fields = '__all__'

class StockInfoSerializers(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['StockNo']

class StockWorkerSerializers(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['StockWorker']

class OrderToStockSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('OrderNo', 'OrderDate', 'Client', 'OrderWeight', 'OrderPrice', 'Part')

class OrderDeleteSerializers(serializers.Serializer):
    OrderNo = serializers.CharField(max_length=255)
    # Method = serializers.CharField(max_length=10)

class StockToProductSerializers(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('OrderNo', 'StockNo','StockDate','StockWorker', 'Stockitem', 'RealWeight', 'RealPrice', 'MeterialNo', 'SlaugtherDate', 'UnitPrice')

class ProductSerializers(serializers.ModelSerializer):
    Method = serializers.CharField(max_length=10)
    class Meta:
        model = Product
        fields = '__all__'

class ProductInfoSerializers(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductDeleteSerializer(serializers.Serializer):
    ProductNo = serializers.CharField(max_length=30)
    Method = serializers.CharField(max_length=10)


class ClientSerializers(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

class ClientInfoSerializers(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['ClientName']

class DeliveryAccidentSerializers(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAccident
        fields = '__all__'

class PurchaseSerializers(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'
