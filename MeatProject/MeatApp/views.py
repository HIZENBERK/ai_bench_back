from django.http import JsonResponse
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, generics
from rest_framework.authtoken.admin import User
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Order, Stock, Product, Client, MeatPart
from .serializers import Userserializers, OrderSerializers, StockSerializers, LoginSerializer, \
    MyTokenObtainPairSerializer, SingupSerializer, ClientSerializers, MeatPartSerializers, MeatPartInfoSerializers, \
    ClientInfoSerializers, OrderInfoSerializers, StockWorkerSerializers, ProductInfoSerializers, \
    StockToProductSerializers, OrderToStockSerializers, StockInfoSerializers, ProductSerializers, ProductDeleteSerializer


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
    @swagger_auto_schema(
        operation_id="제품 생성, 삭제, 수정",
        operation_description="Create, update or delete a product based on the 'Method' field in the request body.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'Method': openapi.Schema(type=openapi.TYPE_STRING, description="'post', 'put', or 'delete'"),
                'StockNo': openapi.Schema(type=openapi.TYPE_STRING, description="Stock number"),
                'ProductWorker': openapi.Schema(type=openapi.TYPE_STRING, description="Product worker"),
                'WeightAfterWork': openapi.Schema(type=openapi.TYPE_STRING, description="Weight after work"),
                'LossWeight': openapi.Schema(type=openapi.TYPE_STRING, description="Loss weight"),
                'ProductPrice': openapi.Schema(type=openapi.TYPE_STRING, description="Product price"),
                'DiscountRate': openapi.Schema(type=openapi.TYPE_STRING, description="Discount rate"),
                'ProductSituation': openapi.Schema(type=openapi.TYPE_STRING, description="Product situation"),
                'Quantity': openapi.Schema(type=openapi.TYPE_STRING, description="Quantity"),
                'ProductNo': openapi.Schema(type=openapi.TYPE_STRING, description="Product number for delete method")
            },
            required=['Method']
        ),
        responses={
            201: 'message: 제품 업데이트 완료',
            204: 'message: 제품 삭제 완료',
            400: 'Bad Request'
        },
        examples={
            'post': {
                'Method': 'post',
                'StockNo': 1,
                'ProductWorker': 'Worker1',
                'WeightAfterWork': 50.5,
                'LossWeight': 5.5,
                'ProductPrice': 100.0,
                'DiscountRate': 10,
                'ProductSituation': 'New',
                'Quantity': 10
            },
            'put': {
                'Method': 'put',
                'StockNo': 1,
                'ProductWorker': 'Worker1',
                'WeightAfterWork': 50.5,
                'LossWeight': 5.5,
                'ProductPrice': 100.0,
                'DiscountRate': 10,
                'ProductSituation': 'Updated',
                'Quantity': 15
            },
            'delete': {
                'Method': 'delete',
                'ProductNo': 1
            }
        }
    )
    def post(self, request):
        if request.data['Method'] == 'post':
            serializer = ProductSerializers(data=request.data)
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
                return JsonResponse({'error': '제품 시리얼라이즈 실패.'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.data['Method'] == 'delete':
            serializer = ProductDeleteSerializer(data=request.data)
            if serializer.is_valid():
                try:
                    productNo = serializer.validated_data.get('ProductNo')
                    # productNo에 해당하는 Product 객체 가져오기
                    product = get_object_or_404(Product, ProductNo=productNo)
                    product.delete()
                    return Response({'message': '제품 삭제 완료'}, status=status.HTTP_204_NO_CONTENT)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'error': '제품 시리얼라이즈 실패.'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.data['Method'] == 'put':
            serializer = ProductSerializers(data=request.data)
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
                    return JsonResponse({'message': '제품 업데이트 완료'}, status=status.HTTP_201_CREATED)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return JsonResponse({'error': '제품 시리얼라이즈 실패.'}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="생성된 제품 정보 불러오기",
        responses={200: ProductInfoSerializers(many=True)}
    )
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

# class ProductDeleteView(APIView):
#     def delete(self, request):
#         serializer = ProductInfoSerializers(data=request.data)
#         if serializer.is_valid():
#             productNo = serializer.validated_data.get('ProductNo')
#             # productNo에 해당하는 Product 객체 가져오기
#             product = get_object_or_404(Product, ProductNo=productNo)
#             product.delete()
#             return Response({'message': '제품 삭제 완료'}, status=status.HTTP_204_NO_CONTENT)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
    @swagger_auto_schema(
        operation_id="로그인",
        operation_description="사원 번호, 비밀번호로 로그인 시 토큰값 반환",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'empNo': openapi.Schema(type=openapi.TYPE_STRING, description="employee number"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="Pass word"),
            },
            required=['empNo', 'password']
        ),
        responses={
            201:  openapi.Response(
                description="로그인 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                        'empNo': openapi.Schema(type=openapi.TYPE_STRING, description='Employee number'),
                        'job': openapi.Schema(type=openapi.TYPE_STRING, description='Job title'),
                        'position': openapi.Schema(type=openapi.TYPE_STRING, description='Position'),
                    }
                )
            ),
            400: openapi.Response(description='잘못된 요청',examples={'application/json': {'serializer.errors': 'error message'}}),
            401: openapi.Response(description='잘못된 자격 증명',examples={'application/json': {'error': 'Invalid credentials'}}),
            403: openapi.Response(description='비활성 사용자', examples={'application/json': {'error': 'Inactive user'}}),
        },
        examples={
            'post': {
                'empNo': 12345,
                'password': 'los23452',
            }
        }
    )
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

    @swagger_auto_schema(
        operation_id="로그아웃",
        operation_description="토큰 번호로 로그아웃 시 로그아웃 성공 ",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description="refresh_token"),
            },
            required=['refresh_token']
        ),
        responses={
            205: openapi.Response(description='로그아웃 성공', examples={'application/json': {'serializer.message': '로그아웃 성공!'}}),
            400: openapi.Response(description='잘못된 요청입니다.', examples={'application/json': {'serializer.errors': "잘못된 요청입니다. + string"}})
        },
        examples={
            'post': {
                'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
            }
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "로그아웃 성공!"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "잘못된 요청입니다."+str(e)}, status=status.HTTP_400_BAD_REQUEST)