from rest_framework import serializers
from store.models import Product,CartItem,Order,OrderItem,Review,ShippingAddress
from django.contrib.auth.models import User
from django.db.models import Avg


class ProductSerializer(serializers.ModelSerializer):
    average_rating=serializers.SerializerMethodField()
    class Meta:
        model=Product
        fields='__all__'

    def get_average_rating(self,obj):
        avg=obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username','password']
        extra_kwargs={'password':{'write_only':True}}

class CartItemSerializer(serializers.ModelSerializer):
    product_detail=ProductSerializer(source='product',read_only=True)
    class Meta:
        model=CartItem
        fields=['id', 'product', 'product_detail', 'quantity']

class OrderItemSerializer(serializers.ModelSerializer):
    product_detail=ProductSerializer(source='product',read_only=True)
    class Meta:
        model=OrderItem
        fields=['product', 'product_detail', 'quantity', 'price']

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['country', 'state', 'city', 'pincode', 'address_line']

class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True,read_only=True)
    class Meta:
        model=Order
        fields=['id', 'total_price', 'payment_status', 'delivery_status', 'ordered_at', 'items']

class ReviewSerializer(serializers.ModelSerializer):
    user_name=serializers.CharField(source='user.username',read_only=True)
    class Meta:
        model=Review
        fields=['id', 'user_name', 'rating', 'comment', 'reviewed_at']