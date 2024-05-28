from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework import viewsets, status, generics
from rest_framework.authtoken.admin import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Order, Stock, Product
from .serializers import Userserializers, Orderserializers, Stockserializers, Productserializers, LoginSerializer, \
    MyTokenObtainPairSerializer, SingupSerializer


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
        serializer = SingupSerializer(data=request.data)
        if serializer.is_valid():
            user = User(
                username=serializer.validated_data['username'],
                Job=serializer.validated_data['Job'],
                Position=serializer.validated_data['Position']
            )
            user.empNo = user.generate_emp_no()
            password = user.generate_password()
            user.set_password(password)
            user.save()

            return JsonResponse({
                'username': user.username,
                'empNo': user.empNo,
                'password': password
            }, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SingupSerializer

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            empNo = serializer.validated_data['empNo']
            password = serializer.validated_data['password']
            user = User.objects.filter(empNo=empNo).first()

            if user and user.check_password(password):
                if user.is_active:
                    refresh = RefreshToken.for_user(user)
                    print(str(refresh.access_token))
                    return JsonResponse({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'username': user.username,
                        'empNo': user.empNo,
                        'job': user.Job,
                        'position': user.Position
                    })
                else:
                    return JsonResponse({'error': 'Inactive user'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# def empinfo_view(request):
#     data = {"message": "This is the empinfo page."}
#     return JsonResponse(data)
