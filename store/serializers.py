from django.db import transaction
from django.db.models import F
from rest_framework import serializers

from store.models import (Address, Cart, CartItem, Collection, Customer, Order,
                          OrderItem, Product)


class SimpleCustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)

    class Meta:
        model = Customer
        fields = ['first_name','last_name','phone','sex','birth_date']

class AddressSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(read_only=True)
    class Meta:
        model = Address
        fields = ['id','customer','label','street','city','state','country']
    def create(self, validated_data):
        user_id = self.context['user_id']
        customer_id = Customer.objects.only('id').prefetch_related('user').get(user_id=user_id)
        self.instance = Address.objects.prefetch_related('customer').create(customer=customer_id,**validated_data)
        return self.instance

class MinifyCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer 
        fields = ['id','first_name','last_name',]


class CollectionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    products_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Collection
        fields = ['id','title','products_count']

class SimpleCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id','title']

class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    collection = SimpleCollectionSerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id','title','collection','unit_price','old_unit_price','stock','description']

class AddProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Product
        fields = ['id','title','collection','unit_price','old_unit_price','stock','description']

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    product = SimpleProductSerializer(read_only=True)
    sub_total_price = serializers.SerializerMethodField()

    def get_sub_total_price(self,cartitem:CartItem):
        return cartitem.product.unit_price * cartitem.quantity
    
    class Meta:
        model = CartItem
        fields = ['id','product','quantity','sub_total_price']

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['id','product_id','quantity']

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        quantity = self.validated_data['quantity']
        product_id = self.validated_data['product_id']
        try: 
            cart_item = CartItem.objects.prefetch_related('cart').select_related('product').get(cart_id=cart_id,product_id=product_id)
            cart_item.quantity += quantity
            self.instance = cart_item.save()
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.prefetch_related('cart').select_related('product').create(cart_id=cart_id,**self.validated_data)
        return self.instance

class UpdateCartItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['id','quantity']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    customer = MinifyCustomerSerializer(read_only=True)
    items = CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self,cart:Cart):
        return sum([item.product.unit_price * item.quantity for item in cart.items.all()])
    
    def create(self, validated_data):
        user_id = self.context.get('user_id')
        self.instance = Cart.objects.select_related('customer__user').prefetch_related('items__product').get(customer__user=user_id)\
        if user_id else Cart.objects.select_related('customer__user').prefetch_related('items__product').create()
        return self.instance
    
    class Meta:
        model = Cart
        fields = ['id','customer','items','total_price']

class MergeAnonymousCartSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        auth_cart = self._get_cart(cart_id=self.context['auth_cart_id'], message='authenticated user')
        anon_cart = self._get_cart(cart_id=self.context['anon_cart_id'], message='anonymous user')

        if auth_cart and anon_cart:
            if auth_cart.id == anon_cart.id:
                raise serializers.ValidationError(\
                    {'error': 'Authenticated and anonymous user carts cannot be merged because they have the same ID.'})

            if anon_cart.customer:
                raise serializers.ValidationError(\
                    {'error': 'The provided cart is not an anonymous cart.'})

            with transaction.atomic():
                for anon_item in anon_cart.items.all():
                    try:
                        auth_item = auth_cart.items.get(product=anon_item.product)
                        auth_item.quantity = F('quantity') + anon_item.quantity
                        auth_item.save(update_fields=['quantity'])
                    except CartItem.DoesNotExist:
                        CartItem.objects.create(cart=auth_cart, product=anon_item.product, quantity=anon_item.quantity)
                    anon_item.delete()
                anon_cart.delete()
                self.instance = auth_cart
                return self.instance
        raise serializers.ValidationError(\
            {'error': 'An authenticated or anonymous user cart is missing, and the merge cannot be completed.'})

    def _get_cart(self, cart_id, message):
        try:
            cart = Cart.objects.get(id=cart_id)
            if not cart.items.exists():
                raise serializers.ValidationError({'error': f"No Product exists for {message} cart"})
            return cart
        except Cart.DoesNotExist:
            raise serializers.ValidationError({'error': f"No cart found with the given {message} cart"})
    
    class Meta:
        model = Cart
        fields = []
    
class OrderItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    product = SimpleProductSerializer(read_only=True)
    sub_total_price = serializers.SerializerMethodField()

    def get_sub_total_price(self,orderitem:OrderItem):
        return orderitem.product.unit_price * orderitem.quantity
    
    class Meta:
        model = OrderItem
        fields = ['id','product','quantity','sub_total_price']

class OrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    items = OrderItemSerializer(many=True,read_only=True)
    customer = MinifyCustomerSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Order 
        fields = ['id','customer','items','status','total_price']

    def get_total_price(self,order:Order):
        return sum([item.product.unit_price * item.quantity for item in order.items.all()])

    def create(self, validated_data):
        user_id = self.context['user_id']
        try:
            customer = Customer.objects.only('id').get(user=user_id)
        except Customer.DoesNotExist:
            raise serializers.ValidationError({'error': 'The user is not associated with any customer account. Please create a customer profile.'})

        try:
            cart = Cart.objects.get(customer__user=user_id)
        except Cart.DoesNotExist:
            raise serializers.ValidationError({'error': 'No cart was found for this customer. Please add items to your cart before creating an order.'})

        with transaction.atomic():
            items = cart.items.all()
            if not items:
                raise serializers.ValidationError({'error': 'The cart is empty. Please add products to your cart before creating an order.'})
            
            for item in items:
                if item.product.stock < item.quantity:
                    raise serializers.ValidationError({'error': f'Product #<{item.id}> - <{item.product}> does not have enough stock available. Please adjust the quantity in your cart.'})
                item.product.stock -= item.quantity
                item.product.save()

            order = Order.objects.create(customer=customer)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in items
            ]
            OrderItem.objects.bulk_create(order_items)
            items.delete()
            self.instance = order
            
        return self.instance