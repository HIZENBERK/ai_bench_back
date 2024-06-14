from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import LoginView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
router = DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'order', views.OrderViewSet)
router.register(r'stock', views.StockViewSet)
router.register(r'product', views.ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', views.LoginView.as_view(), name='admin'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('user/', views.UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('ClientInfo/', views.ClientInfoView.as_view(), name='client_info'),
    path('Client/', views.ClientView.as_view(), name='client'),
    path('MeatPartInfo/', views.MeatPartInfoView.as_view(), name='meat_part_info'),
    path('MeatPart/', views.MeatPartView.as_view(), name='meat_part'),
    path('order/', views.OrderView.as_view(), name='order'),
    path('stock/', views.StockView.as_view(), name='stock'),
    path('stockworker/', views.StockWorkerView.as_view(), name='stockworker'),
    path('product/', views.ProductView.as_view(), name='product'),
]