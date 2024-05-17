from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from rest_framework import viewsets
from .models import EmpInfo, LoginInfo, Order, Stock, Product
from .serializers import EmpInfoserializers, LoginInfoserializers, Orderserializers, Stockserializers, Productserializers

# Create your views here.
class EmpInfoViewSet(viewsets.ModelViewSet):
    queryset = EmpInfo.objects.all()
    serializer_class = EmpInfoserializers

class LoginInfoViewSet(viewsets.ModelViewSet):
    queryset = LoginInfo.objects.all()
    serializer_class = LoginInfoserializers

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = Orderserializers

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = Stockserializers

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = Productserializers

def empinfo_view(request):
    data = {"message": "This is the empinfo page."}
    return JsonResponse(data)