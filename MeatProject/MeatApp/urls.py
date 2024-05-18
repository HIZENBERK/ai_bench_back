from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'empinfo', views.EmpInfoViewSet)
router.register(r'logininfo', views.LoginInfoViewSet)
router.register(r'order', views.OrderViewSet)
router.register(r'stock', views.StockViewSet)
router.register(r'product', views.ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('empinfo/', views.EmpInfoViewSet.as_view({'get': 'list', 'post': 'create'}), name='empinfo-list'),
    path('emminfo/&lt;int:pk&gt;/', views.EmpInfoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='empinfo-detail'),
    path('logininfo/', views.LoginInfoViewSet.as_view({'get': 'list', 'post': 'create'}), name='logininfo-list'),
    path('logininfo/&lt;int:pk&gt;/', views.LoginInfoViewSet.as_view({'get': 'retrieve', 'put': 'update', ' delete': 'destroy'}), name='logininfo-detail'),
    path('order/', views.OrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='order-list'),
    path('order/&lt;int:pk&gt;/', views.OrderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='order-detail'),
    path('stock/', views.StockViewSet.as_view({'get': 'list', 'post': 'create'}), name='stock-list'),
    path('stock/&lt;int:pk&gt;/', views.StockViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='stock-detail'),
    path('product/', views.ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    path('product/&lt;int:pk&gt;/', views.ProductViewSet.as_view({'get': 'retrieve', 'put': 'update', ' delete': 'destroy'}), name='product-detail'),
    
]