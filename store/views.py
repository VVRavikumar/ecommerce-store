from django.shortcuts import render,get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import ListView
from rest_framework.views import APIView
from store.models import Product,CartItem,Order,OrderItem,Review,ShippingAddress
from store.serializers import ProductSerializer, UserSerializer,CartItemSerializer,OrderSerializer,OrderItemSerializer,ReviewSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import generics,status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from store.permissions import IsAdminUser
from rest_framework import viewsets
from django.db.models import Q
from django.views.generic import DetailView
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User

class RegisterView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=400)

        User.objects.create_user(username=username, password=password)
        return Response({'message': 'User created successfully'})


class ProductListAPIView(generics.ListAPIView):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    filter_backends=[DjangoFilterBackend]
    filterset_fields=['category','name']

class ProductListView(ListView):
    model=Product
    template='product_list.html'
    context_object_name='products'
    paginate_by = 6
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')

        queryset = Product.objects.all()

        if query:
            queryset = queryset.filter(name__icontains=query)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

class CartListCreateView(generics.ListCreateAPIView):
    serializer_class=CartItemSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
    
    def perform_create(self,serializer):
        serializer.save(user=self.request.user)

class CartUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class=CartItemSerializer
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)
    
class PlaceOrderView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        cart_items=CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({'detail':'Cart is Empty'},status=400)
        total=sum(item.product.price*item.quantity for item in cart_items)
        payment_method = request.POST.get('payment_method', 'COD')
        order=Order.objects.create(user=request.user,total_price=total,payment_method=payment_method)
        

        for item in cart_items:
            OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
            )

        cart_items.delete()

        return Response({'message':'Order placed','order_id':order.id},status=201)

class OrderListView(generics.ListAPIView):
    serializer_class=OrderSerializer
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
class CreateReviewView(generics.CreateAPIView):
    serializer_class=ReviewSerializer
    permission_classes=[IsAuthenticated]
    def perform_create(self,serializer):
        product_id=self.kwargs['product_id']
        product=get_object_or_404(Product,id=product_id)

        has_ordered=OrderItem.objects.filter(order__user=self.request.user,product=product).exists()

        if not has_ordered:
            raise ValidationError('You can only review products you have purchased.')
        
        serializer.save(user=self.request.user,product=product)

class ProductReviewListView(generics.ListAPIView):
    serializer_class=ReviewSerializer
    def get_queryset(self):
        product_id=self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id)

class AdminProductViewSet(viewsets.ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    permission_classes=[IsAdminUser,IsAuthenticated]

class AdminOrderListView(generics.ListAPIView):
    queryset=Order.objects.all()
    serializer_class=OrderSerializer
    permission_classes=[IsAdminUser,IsAuthenticated]

class AdminOrderUpdateView(generics.UpdateAPIView):
    queryset=Order.objects.all()
    serializer_class=OrderSerializer
    permission_classes=[IsAdminUser,IsAuthenticated]

class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        quantity = int(request.POST.get('quantity', 1))

        cart = request.session.get('cart', {})
        product_id = str(self.object.id)

        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity

        request.session['cart'] = cart
        messages.success(request, f"{self.object.name} added to cart!")
        return redirect('product-detail', pk=self.object.id)

class CartView(View):
    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user)

        # Calculate subtotal for each item
        for item in cart_items:
            item.subtotal = item.product.price * item.quantity

        total = sum(item.subtotal for item in cart_items)

        context = {
            'cart_items': cart_items,
            'total': total
        }
        return render(request, 'store/cart.html', context)

class RemoveFromCartView(View):
    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        
        return redirect('cart')



def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('shop')  # After successful login, go to shop page
        else:
            return render(request, 'store/login.html', {'error': 'Invalid username or password'})

    return render(request, 'store/login.html')


class AddToCartView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product
        )

        if created:
            # New item added, set quantity
            cart_item.quantity = quantity
        else:
            # Already in cart, just add new quantity
            cart_item.quantity += quantity

        cart_item.save()

        return redirect('cart')

class CheckoutView(View):
    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        for item in cart_items:
            item.subtotal = item.product.price * item.quantity
        total = sum(item.product.price * item.quantity for item in cart_items)
        return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total})

    def post(self, request):
        #address = request.POST.get('address')
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect('cart')  # No items to checkout

        total = sum(item.product.price * item.quantity for item in cart_items)
        payment_method = request.POST.get('payment_method', 'COD')
        order = Order.objects.create(user=request.user, total_price=total,payment_method=payment_method)
        

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        ShippingAddress.objects.create(
            user=request.user,
            order=order,
            country=request.POST.get('country'),
            state=request.POST.get('state'),
            city=request.POST.get('city'),
            pincode=request.POST.get('pincode'),
            address_line=request.POST.get('address_line'),
        )
        # Empty the cart
        cart_items.delete()

        return redirect('order-success')  # Redirect after successful checkout

class OrderSuccessView(View):
    def get(self, request):
        return render(request, 'store/order_success.html')

