from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import user, service, items, items_service_price ,order, order_item


class UserCreateSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = user
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'user_type', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user_type = validated_data.pop('user_type','Customer')
        user_instance = user.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            user_type=user_type
        )
        return user_instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'user_type']
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = service
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = items
        fields = '__all__'
        
class ItemsServicePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = items_service_price
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = order_item
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = order
        fields = '__all__'



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user_instance = authenticate(username=username, password=password)
            if user_instance:
                if user_instance.is_active:
                    data['user'] = user_instance
                    return data
                else:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')
