import uuid

from django.conf import settings
from django.contrib import admin
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.

class Customer(models.Model):
    SEX_MALE = 'm'
    SEX_FEMALE = 'f'
    SEX_CHOICES = [
        (SEX_MALE,'Male'),
        (SEX_FEMALE,'Female'),
    ]
    MEMBERSHIP_BRONZE = 'b'
    MEMBERSHIP_SILVER = 's'
    MEMBERSHIP_GOLD = 'g'
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE,'Bronze'),
        (MEMBERSHIP_SILVER,'Silver'),
        (MEMBERSHIP_GOLD,'Gold'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.PositiveIntegerField(blank=True,null=True)
    birth_date = models.DateField(blank=True,null=True)
    sex = models.CharField(choices=SEX_CHOICES,default=SEX_MALE,max_length=1)
    membership = models.CharField(choices=MEMBERSHIP_CHOICES,default=MEMBERSHIP_SILVER, max_length=1)

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}' 
    
    class Meta:
        ordering = ['user__first_name','user__last_name']

class Collection(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return f'{self.title}'
    
    class Meta:
        ordering = ['title']

class Product(models.Model):
    title = models.CharField(max_length=128)
    collection = models.ForeignKey(Collection,on_delete=models.PROTECT,related_name='products')
    unit_price = models.DecimalField(max_digits=10,decimal_places=2)
    old_unit_price = models.DecimalField(max_digits=10,decimal_places=2)
    description = models.TextField()
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'{self.title}'
    
    class Meta:
        ordering = ['title']

class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4,primary_key=True,editable=False)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart #{self.id}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ['cart','product']

class Order(models.Model):
    STATUS_PENDING = 'p'
    STATUS_FAILED = 'f'
    STATUS_CONFIRM = 'c'
    STATUS_COICHES = [
        (STATUS_PENDING,'Pending'),
        (STATUS_FAILED,'Failed'),
        (STATUS_CONFIRM,'Confirm'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=STATUS_COICHES,default=STATUS_PENDING,max_length=1)

    def __str__(self) -> str:
        return f'Order #{self.id} by {self.customer}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT,related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT,related_name='orderitems')
    unit_price = models.DecimalField(max_digits=10,decimal_places=2)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    
    class Meta:
        unique_together = ['order','product']

class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,related_name='addresses')
    label = models.CharField(max_length=32)
    street = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    COUTNRY_BD = 'bd'
    COUTNRY_COICHES = [
        (COUTNRY_BD,'Bangladesh'),
    ]
    country = models.CharField(choices=COUTNRY_COICHES,default=COUTNRY_BD,max_length=2)