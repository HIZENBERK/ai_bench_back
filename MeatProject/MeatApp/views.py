from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.authtoken.admin import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import User, Order, Stock, Product
from .serializers import Userserializers, Orderserializers, Stockserializers, Productserializers, LoginSerializer


# Create your views here.
# class EmpInfoViewSet(viewsets.ModelViewSet):
#     queryset = EmpInfo.objects.all()
#     serializer_class = EmpInfoserializers
#
# class LoginInfoViewSet(viewsets.ModelViewSet):
#     queryset = LoginInfo.objects.all()
#     serializer_class = LoginInfoserializers
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = Userserializers


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
        user = User.objects.create_user(data['UserName'], data['Position'], data['Job'])

        token = Token.objects.create(user=user)
        return Response({"token": token.key})


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            EmpNo = serializer.validated_data['EmpNo']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(EmpNo=EmpNo, password=password)
                if user.check_password(EmpNo,password):
                    return Response({
                        'user_id': user.id,
                        'username': user.username,
                        'EmpNo': user.EmpNo
                    })
                else:
                    return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({'error': 'Invalid EmpNo'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# def empinfo_view(request):
#     data = {"message": "This is the empinfo page."}
#     return JsonResponse(data)
