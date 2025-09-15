from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView
)
from .views import (
    UserView, 
    ServiceView, 
    ItemView,
    ItemsServicePriceView,
    OrderView, 
    OrderItemView, 
    LoginView, 
    ProfileView,
    SendDeliveryOtpView,
    VerifyDeliveryOtpView,
    StaffOrderListView
)


urlpatterns = [
    path('users/', UserView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='user-list-create'),
    path('users/<int:pk>/', UserView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='user-detail'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # Service endpoints
    path('services/', ServiceView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='service-list-create'),
    path('services/<int:pk>/', ServiceView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='service-detail'),
    
    # Item endpoints
    path('items/', ItemView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='item-list-create'),
    path('items/<int:pk>/', ItemView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='item-detail'),
    
    path('items-service-price/', ItemsServicePriceView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='items-service-price-list-create'),
    
    # Order endpoints
    path('orders/', OrderView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='order-list-create'),
    path('orders/<int:pk>/', OrderView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='order-detail'),
    
    # Order Item endpoints
    path('order-items/', OrderItemView.as_view({
        'get': 'list',
        'post': 'create'
    }), name='order-item-list-create'),
    
    path('order-items/<int:pk>/', OrderItemView.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='order-item-detail'),

    path('staff-order-list/', StaffOrderListView.as_view(), name='staff-order-list'),

    path('send-delivery-otp/<int:order_id>/', SendDeliveryOtpView.as_view(), name='send-delivery-otp'),
    path('verify-delivery-otp/<int:order_id>/', VerifyDeliveryOtpView.as_view(), name='verify-delivery-otp'),
]
