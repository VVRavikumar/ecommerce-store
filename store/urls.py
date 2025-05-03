from django.urls import path,include
from store import views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework.routers import DefaultRouter

router=DefaultRouter()
router.register('admin/products',views.AdminProductViewSet,basename='admin-products')


urlpatterns=[
    path('register/',views.RegisterView.as_view(),name='register'),
    path('token/',TokenObtainPairView.as_view(),name='token'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token'),
    path('products/',views.ProductListAPIView.as_view(),name='product-list-api'),
    #path('cart/',views.CartListCreateView.as_view(), name='cart-list'),
    path('cart/<int:pk>/',views.CartUpdateDeleteView.as_view(), name='cart-detail'),
    path('orders/place/',views.PlaceOrderView.as_view(),name='place-order'),
    path('orders/',views.OrderListView.as_view(),name='orders'),
    path('products/<int:product_id>/review/',views.CreateReviewView.as_view(),name='create-review'),
    path('products/<int:product_id>/reviews/',views.ProductReviewListView.as_view(),name='product-reviews'),
    path('',include(router.urls)),
    path('admin/orders/', views.AdminOrderListView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:pk>/', views.AdminOrderUpdateView.as_view(), name='admin-order-update'),
    path('shop/', views.ProductListView.as_view(), name='shop'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.AddToCartView.as_view(), name='add-to-cart'),

    path('cart/remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('login/', views.user_login, name='login'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order-success/', views.OrderSuccessView.as_view(), name='order-success'),
]