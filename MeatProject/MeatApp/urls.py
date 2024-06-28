from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
router = DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'order', views.OrderViewSet)
router.register(r'stock', views.StockViewSet)

schema_view = get_schema_view(
   openapi.Info(
      title="모던한담 API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   validators=['flex', 'ssv'],
   public=True,
   permission_classes=(AllowAny,)
)

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
    path('stockInfo/', views.StockInfoView.as_view(), name='stock_info'),
    path('stockworker/', views.StockWorkerView.as_view(), name='stockworker'),
    path('incoming/', views.IncomingPage, name='IncomingPage'),
    path('product/', views.ProductView.as_view(), name='product'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]