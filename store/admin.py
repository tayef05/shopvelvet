from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from store.models import (Address, Cart, CartItem, Collection, Customer, Order,
                          OrderItem, Product)

# Register your models here.

class StockStatusFilter(admin.SimpleListFilter):
    title = 'stock status'
    parameter_name = 'stock_status'
    def lookups(self, request, model_admin):
        return [
            ('h','High'),
            ('l','Low'),
            ('m','Medium'),
        ]
    def queryset(self, request, queryset):
        if self.value() == 'l':
            return queryset.filter(stock__lte=int(10))
        if self.value() == 'm':
            return queryset.filter(stock__gte=int(11),stock__lte=int(49))
        if self.value() == 'h':
            return queryset.filter(stock__gte=int(50))
        
class AnonymousCartFilter(admin.SimpleListFilter):
    title = 'customer'
    parameter_name = 'customer'

    def lookups(self, request, model_admin):
        return [
            ('an','Anonymous'),
            ('au','Authenticated'),
                ]
    def queryset(self, request, queryset):
        if self.value() == 'an':
            return queryset.filter(customer__isnull=True)
        if self.value() == 'au':
            return queryset.filter(customer__isnull=False)
    

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    readonly_fields = ['user']
    list_display = ['first_name','last_name','phone','sex','membership','orders']
    list_editable = ['membership']
    list_filter = ['birth_date','membership','sex']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['user__first_name','user__last_name','phone']
    list_select_related = ['user']
    list_per_page = 10

    @admin.display(ordering='orders_count')
    def orders(self,customer):
        url = reverse('admin:store_order_changelist') + "?" + urlencode({'customer__id':str(customer.id)})
        return format_html("<a href='{}'>{}</a>",url,customer.orders_count)
    
    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).annotate(orders_count=Count('order'))

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']
    search_fields = ['title__istartswith']

    def products_count(self,collection):
        url = reverse('admin:store_product_changelist') + '?' + urlencode({'collection__id':str(collection.id)})
        return format_html("<a href='{}'>{}</a>",url,collection.product_count)
    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).annotate(product_count=Count('products'))

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']
    actions = ['clear_stock']
    list_display = ['title','unit_price','old_unit_price','stock_status','collection_title']
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ['title']
    list_editable = ['unit_price','old_unit_price',]
    list_filter = ['collection',StockStatusFilter,]

    @admin.display(ordering='collection__title')
    def collection_title(self,product:Product):
        return product.collection.title
    
    def stock_status(self,product:Product):
        if product.stock <= 10:
            return 'Low'
        return 'Ok'
 
    @admin.action(description='Clear stock')
    def clear_stock(self,request,queryset):
        updated_count = queryset.update(stock=0)
        self.message_user(request,f'{updated_count} products were successfully updated.',messages.ERROR)

class CartItemInline(admin.TabularInline):
    model = CartItem
    min_num = 1
    extra = 1
    autocomplete_fields = ['product']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id','customer_name','created_at']
    inlines = [CartItemInline]
    list_filter = [AnonymousCartFilter,'created_at']
    list_per_page = 10
    list_select_related = ['customer']
    autocomplete_fields = ['customer']

    @admin.display(ordering='customer')
    def customer_name(self,cart:Cart):
        if not cart.customer:
            return cart.customer
        url = reverse('admin:store_customer_changelist') + '?' + urlencode({'id':str(cart.customer.pk)})
        return format_html('<a href="{}">{}</a>',url,cart.customer)

class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    extra = 1
    model = OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_editable = ['status']
    list_display = ['id','customer_name','status','created_at']
    list_filter = ['status','created_at','update_at']
    list_per_page = 10

    @admin.display(ordering='customer')
    def customer_name(self,order:Order):
        url = reverse('admin:store_customer_changelist') + '?' + urlencode({'id':str(order.customer.pk)})
        return format_html('<a href="{}">{}</a>',url,order.customer)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['id','customer_name','street','city','state','country',]
    autocomplete_fields = ['customer',]
    list_editable = ['street',]
    list_filter = ['city','state','country']

    def customer_name(self,address:Address):
        url = reverse('admin:store_customer_changelist') + '?' + urlencode({'id':address.customer.pk})
        return format_html('<a href="{}">{}</a>',url,address.customer)