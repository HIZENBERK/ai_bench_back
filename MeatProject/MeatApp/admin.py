from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import User, Order, Stock, Product, Purchase, DeliveryAccident, InOutCome, Client, MeatPart, OtherCost
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _


# 모델을 관리자 페이지에 등록합니다.

admin.site.register(User)
admin.site.register(Order)
admin.site.register(Stock)
admin.site.register(Product)
admin.site.register(Client)
admin.site.register(MeatPart)
admin.site.register(Purchase)
admin.site.register(DeliveryAccident)
#admin.site.register(InOutCome)
admin.site.register(OtherCost)


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('empNo', 'username', 'is_active', 'is_staff', 'date_joined', 'Job', 'Position')
    list_display_links = ('empNo',)
    list_filter = ('is_active', 'is_staff', 'Job', 'Position')
    fieldsets = (
        ('개인 정보', {'fields': ('empNo', 'username', 'Job', 'Position')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('중요 날짜', {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('empNo', 'username', 'Job', 'Position', 'password1', 'password2')}
         ),
    )
    search_fields = ('empNo', 'username')
    ordering = ('-date_joined',)
    filter_horizontal = ()