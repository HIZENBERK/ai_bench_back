from django.http import JsonResponse
from rest_framework import viewsets, status, generics
from rest_framework.authtoken.admin import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Order, Stock, Product, Client, MeatPart
from .serializers import Userserializers, OrderSerializers, StockSerializers, ProductSerializers, LoginSerializer, \
    MyTokenObtainPairSerializer, SingupSerializer, ClientSerializers, MeatPartSerializers, MeatPartInfoSerializers, ClientInfoSerializers

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = Userserializers


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializers


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializers


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializers


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


class OrderView(APIView):
    # def post(self, request):
    #     serializer = OrderSerializers(data=request.data)
    #     if serializer.is_valid():
    #         order = Order(
    #             EmpNo=serializer.validated_data['empNo'],
    #             OrderDate=serializer.validated_data['OrderDate'],
    #             OrderWeight=serializer.validated_data['OrderWeight'],
    #             ETA = serializer.validated_data['OrderWeight'],
    #             Part = serializer.validated_data['OrderWeight'],
    #             Client = serializer.validated_data['OrderWeight'],
    #             OderPrice = serializer.validated_data['OrderWeight'],
    #         )
    #         order.EmpNo = User.empNo()
    #         order.save()
    #
    #         return JsonResponse({
    #             'empNo': order.EmpNo,
    #         }, status=status.HTTP_201_CREATED)
    #     return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        queryset = Order.objects.all()
        serializer = OrderSerializers(queryset, many=True)
        print(serializer.data)
        return JsonResponse(serializer.data, safe=False)

class ClientInfoView(APIView):
    def get(self, request):
        queryset = Client.objects.all()
        serializer = ClientInfoSerializers(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

class ClientView(APIView):
    def get(self, request):
        queryset = Client.objects.all()
        serializer = ClientSerializers(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)
class MeatPartInfoView(APIView):
    def get(self, request):
        queryset = MeatPart.objects.all()
        serializer = MeatPartInfoSerializers(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)
class MeatPartView(APIView):
    def get(self, request):
        queryset = MeatPart.objects.all()
        serializer = MeatPartSerializers(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

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

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        print(request.data["refreshToken"])
        try:
            refresh_token  = request.data["refresh_token "]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)