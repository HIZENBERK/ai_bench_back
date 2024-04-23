from django.contrib import admin
from .models import EmpInfo, LoginInfo, Order, Stock, Product


# Register your models here.

admin.site.register(EmpInfo)
admin.site.register(LoginInfo)
admin.site.register(Order)
admin.site.register(Stock)
admin.site.register(Product)
