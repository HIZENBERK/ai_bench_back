from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Order, Stock, Product


# Register your models here.

# admin.site.register(EmpInfo)
# admin.site.register(LoginInfo)
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Order)
admin.site.register(Stock)
admin.site.register(Product)
