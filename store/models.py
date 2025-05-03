from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    name=models.CharField(max_length=50)
    description=models.TextField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    category=models.CharField(max_length=50)
    image=models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name
    
class CartItem(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='cart_items')
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    added_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('user','product')
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} x {self.quantity}"
    
class Order(models.Model):
    STATUS_CHOICES=[
        ('Pending','Pending'),
        ('Failed','Failed'),
        ('Paid','Paid'),
    ]
    DELIVERY_CHOICES=[
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]
    #shipping_address = models.TextField(blank=True, null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='orders')
    total_price=models.DecimalField(max_digits=10,decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[('COD', 'Cash on Delivery'), ('Online', 'Online Payment')], default='COD')
    payment_status=models.CharField(max_length=50,choices=STATUS_CHOICES,default='Pending')
    delivery_status=models.CharField(max_length=50,choices=DELIVERY_CHOICES,default='Pending')
    ordered_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    
class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()
    price=models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_address')
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    address_line = models.TextField()

    def __str__(self):
        return f"{self.address_line}, {self.city}"
    
class Review(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='reviews')
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='reviews')
    rating=models.PositiveIntegerField()
    comment=models.TextField(blank=True)
    reviewed_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together=('user','product')
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating})"