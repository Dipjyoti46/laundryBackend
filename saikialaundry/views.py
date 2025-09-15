from rest_framework.response import Response
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import generics, mixins, viewsets
from rest_framework import viewsets as rest_viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import user, service, items, items_service_price, order, order_item
import random
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    ServiceSerializer, 
    ItemSerializer, 
    ItemsServicePriceSerializer,
    OrderSerializer, 
    OrderItemSerializer, 
    LoginSerializer
)
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
#=== Login API ===
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'status': True,
                'message': 'Login successful',
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'user_type': user.user_type,
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }
            }, status=200)
        return Response(
            {
                'status': False,
                'data': {},
                'message': 'Log in failed, Invalid credentials'
            }, status=401
        )
#=== Profile View ===
class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        self.request.user
        serializer = UserSerializer(request.user)
        return Response({
            'status': True,
            'message': 'Profile retrieved successfully',
            'data': serializer.data
        }, status=200)

# === USER VIEW ===
class UserView(rest_viewsets.ModelViewSet):
    queryset = user.objects.all()
    lookup_field = 'username'
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return []  # No authentication needed for registration
        return [IsAuthenticated()]

    def get_object(self):
        if self.kwargs.get('username') == 'me':
            return self.request.user
        return super().get_object()
     
# === SERVICE VIEW ===
class ServiceView(viewsets.ModelViewSet):
    queryset = service.objects.all()
    serializer_class = ServiceSerializer
    # permission_classes = [IsAuthenticated]


# === ITEM VIEW ===
class ItemView(viewsets.ModelViewSet):
    queryset = items.objects.all()
    serializer_class = ItemSerializer
    # permission_classes = [IsAuthenticated]
#

# === ITEMS SERVICE PRICE VIEW ===
class ItemsServicePriceView(viewsets.ModelViewSet):
    queryset = items_service_price.objects.all()
    serializer_class = ItemsServicePriceSerializer
    # permission_classes = [IsAuthenticated]
    
# === ORDER VIEW ===
class OrderView(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'DeliveryPerson':
            # Delivery staff see orders that need pickup or delivery
            return order.objects.filter(
                order_status__in=[
                    'Order Confirmed',  # Ready for pickup
                    'Out for pickup',   # Currently being picked up
                    'Picked Up',        # Already picked up
                    'In Progress',      # Being processed
                    'Out for Delivery'  # Ready for delivery
                ]
            ).order_by('-order_date')
        elif user.is_staff:
            # Admins can see all orders
            return order.objects.all().order_by('-order_date')
        else:
            # Regular users only see their own orders
            return order.objects.filter(user=user).order_by('-order_date')
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# === ORDER ITEM VIEW ===
class OrderItemView(viewsets.ModelViewSet):
    queryset = order_item.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
# ==== Staff Order List View ===

class StaffOrderListView(generics.ListAPIView):
    queryset = order.objects.all().order_by('-order_date')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

# ==== Delivery OTP ====
# Step 1: Send OTP
class SendDeliveryOtpView(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order_obj = order.objects.get(order_id=order_id)
            email = user.objects.get(id=order_obj.user_id).email

            # Generate OTP directly here
            otp = str(random.randint(100000, 999999))
            order_obj.delivery_otp = otp
            order_obj.save()

            # Send OTP via email
            send_mail(
                subject="Your Delivery OTP",
                message=f"Your OTP for order {order_obj.order_id} is {otp}. Share it with the delivery person to confirm delivery.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            return Response({"message": "OTP sent to customer"}, status=status.HTTP_200_OK)

        except order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


# Step 2: Verify OTP & Mark Delivered
class VerifyDeliveryOtpView(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order_obj = order.objects.get(order_id=order_id)
            entered_otp = request.data.get("otp")
            original_otp = order_obj.delivery_otp

            if original_otp == entered_otp:
                order_obj.order_status = "Delivered"
                order_obj.delivery_otp = None  # Clear OTP after success
                order_obj.save()
                return Response({"message": "Order marked as Delivered"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP", "original-otp": original_otp, "entered_otp": entered_otp}, status=status.HTTP_400_BAD_REQUEST)

        except order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

