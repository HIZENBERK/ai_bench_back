from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import CustomUser, Order, Stock, Product
from .serializers import CustomUserserializers, Orderserializers, Stockserializers, Productserializers

# Create your views here.
# class EmpInfoViewSet(viewsets.ModelViewSet):
#     queryset = EmpInfo.objects.all()
#     serializer_class = EmpInfoserializers
#
# class LoginInfoViewSet(viewsets.ModelViewSet):
#     queryset = LoginInfo.objects.all()
#     serializer_class = LoginInfoserializers
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserserializers
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = Orderserializers

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = Stockserializers

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = Productserializers
    
    
# 토큰을 이용한 회원가입
class SignupView(APIView):
    def post(self, request):
        data = request.data
        user = CustomUser.objects.create_user(data['EmpNo'], data['PassWord'])

        token = Token.objects.create(user=user)
        return Response({"token": token.key})
    

# def empinfo_view(request):
#     data = {"message": "This is the empinfo page."}
#     return JsonResponse(data)