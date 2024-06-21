from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import BaseDeleteView
from rest_framework import viewsets, status, generics
from rest_framework.authtoken.admin import User
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.utils import datetime_from_epoch
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Order, Stock, Product, Client, MeatPart
from .serializers import Userserializers, OrderSerializers, StockSerializers, LoginSerializer, \
    MyTokenObtainPairSerializer, SingupSerializer, ClientSerializers, MeatPartSerializers, MeatPartInfoSerializers, \
    ClientInfoSerializers, OrderInfoSerializers, StockWorkerSerializers, ProductInfoSerializers, \
    StockToProductSerializers, OrderToStockSerializers, StockInfoSerializers


def IncomingPage(request):
    return render(request, 'IncomingPage.js')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = Userserializers


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializers


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializers


# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializers


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
    def post(self, request):
        serializer = OrderSerializers(data=request.data)
        if serializer.is_valid():
            try:
                order = Order.objects.create(
                    Part=serializer.validated_data['Part'], # MeatPart의 code를 Order의 Part에 할당
                    OrderDate=serializer.validated_data['OrderDate'],
                    OrderWorker=serializer.validated_data['OrderWorker'],
                    ETA=serializer.validated_data['ETA'],
                    Client=serializer.validated_data['Client'],
                    OrderWeight=serializer.validated_data['OrderWeight'], 
                    OrderPrice=serializer.validated_data['OrderPrice'],
                    OrderSituation='발주완료'  # 상태
                )
                order.save()
                return JsonResponse({'message': '발주 생성 완료'}, status=status.HTTP_201_CREATED)
            except MeatPart.DoesNotExist:
                return JsonResponse({'error': '부위 참조 생성 실패.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'error': '발주 생성 실패.'}, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        queryset = Order.objects.all()
        serializer = OrderInfoSerializers(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

class StockView(APIView):
    def get(self, request):
        queryset = Stock.objects.all()
        serializer = StockSerializers(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        order_no = request.data.get('OrderNo')
        try:
            order = Order.objects.get(OrderNo=order_no)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_400_BAD_REQUEST)

        stock_data = request.data
        stock_data['OrderNo'] = order.OrderNo  # Replace OrderNo with the order instance

        serializer = StockSerializers(data=stock_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StockInfoView(APIView):
    def get(self, request):
        queryset = Stock.objects.all()
        serializer = StockInfoSerializers(queryset, many=True)
        return JsonResponse(serializer.data, safe=False)

class StockWorkerView(APIView):
    def get(self, request):
        queryset = Stock.objects.all()
        serializer = StockWorkerSerializers(queryset, many=True)
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

class ProductView(APIView):
    def post(self, request):
        serializer = ProductInfoSerializers(data=request.data)
        if serializer.is_valid():
            try:
                product = Product.objects.create(
                    StockNo=serializer.validated_data['StockNo'],
                    ProductWorker=serializer.validated_data['ProductWorker'],
                    WeightAfterWork=serializer.validated_data['WeightAfterWork'],
                    LossWeight=serializer.validated_data['LossWeight'],
                    ProductPrice=serializer.validated_data['ProductPrice'],
                    DiscountRate=serializer.validated_data['DiscountRate'],
                    ProductSituation=serializer.validated_data['ProductSituation'],
                    Quantity=serializer.validated_data['Quantity']
                )
                product.save()
                return JsonResponse({'message': '제품 생성 완료'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'error': '제품 생성 실패.' + str(Exception)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        product_data = Product.objects.all()
        serializer = ProductInfoSerializers(product_data, many=True)

        for item in serializer.data:
            stock_no = item['StockNo']
            try:
                stock_link_data = Stock.objects.get(StockNo=stock_no)
                stock_serializer = StockToProductSerializers(stock_link_data)
                order_link_data = Order.objects.get(OrderNo=stock_link_data.OrderNo)
                order_serializer = OrderToStockSerializers(order_link_data)
                try:
                    part_link_data = MeatPart.objects.get(code=order_serializer.data['Part'])
                    part_serializer = MeatPartInfoSerializers(part_link_data)
                    item['Part'] = part_serializer.data['name']
                except MeatPart.DoesNotExist:
                    item['Part'] = 'Part not found'

                item['OrderDate'] = order_serializer.data['OrderDate']
                item['Client'] = order_serializer.data['Client']
                item['OrderWeight'] = order_serializer.data['OrderWeight']
                item['OrderPrice']=order_serializer.data['OrderPrice']
                item['StockDate'] = stock_serializer.data['StockDate']
                item['StockWorker'] = stock_serializer.data['StockWorker']
                item['Stockitem'] = stock_serializer.data['Stockitem']
                item['RealWeight']=stock_serializer.data['RealWeight']
                item['RealPrice']=stock_serializer.data['RealPrice']
                item['MeterialNo']=stock_serializer.data['MeterialNo']
                item['SlaugtherDate']=stock_serializer.data['SlaugtherDate']
                item['UnitPrice']=stock_serializer.data['UnitPrice']
                item['MeterialNo'] = stock_serializer.data['MeterialNo']
            except Stock.DoesNotExist:
                item['link_data'] = 'Stock data not found'
            except Order.DoesNotExist:
                item['link_data'] = 'Order data not found'

        return JsonResponse(serializer.data, safe=False)

class ProductDeleteView(APIView):
    def post(self, request):
        serializer = ProductInfoSerializers(data=request.data)
        if serializer.is_valid():
            try:
                productNo = request.data.get('ProductNo')
                # productNo에 해당하는 Product 객체 가져오기
                product = get_object_or_404(Product, ProductNo=productNo)
                product.delete()
                return JsonResponse({'message': '제품 삭제 완료'}, status=status.HTTP_204_NO_CONTENT)
            except Product.DoesNotExist:
                return JsonResponse({'error': '해당 제품이 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
                    access_token = refresh.access_token
                    # print('refresh : '+str(refresh))
                    # print('access_token : '+str(access_token))
                    return JsonResponse({
                        'refresh': str(refresh),
                        'access': str(access_token),
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
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "로그아웃 성공!"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "잘못된 요청입니다."+str(e)}, status=status.HTTP_400_BAD_REQUEST)