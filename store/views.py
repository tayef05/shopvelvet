from django.db.models import Q
from django.db.models.aggregates import Count
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin, UpdateModelMixin)
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from store.models import (Address, Cart, CartItem, Collection, Customer, Order,
                          Product)
from store.permissions import (AllowUnauthenticatedForCart, IsAdminOrReadOnly,
                               StaffUpdatePermission)
from store.serializers import (AddCartItemSerializer, AddProductSerializer,
                               AddressSerializer, CartItemSerializer,
                               CartSerializer, CollectionSerializer,
                               MergeAnonymousCartSerializer, OrderSerializer,
                               ProductSerializer, SimpleCustomerSerializer,
                               UpdateCartItemSerializer)


# Create your views here.
class AddressViewset(ModelViewSet):
    http_method_names = ['get','post','patch','delete','head','options']
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    def get_serializer_context(self):
        return {'user_id':self.request.user.id}
    def get_queryset(self):
        user = self.request.user
        common_query = Address.objects.select_related('customer__user').all()
        return common_query.filter(Q() if user.is_staff else Q(customer__user=user.id) )

class CustomerViewset(ModelViewSet):
    serializer_class = SimpleCustomerSerializer
    permission_classes = [IsAuthenticated]
    def create(self, request, *args, **kwargs):
        if request.method == 'POST' and not request.user.is_staff:
            raise MethodNotAllowed(method='post')
        return super().create(request, *args, **kwargs)
    def get_queryset(self):
        user = self.request.user
        common_query = Customer.objects.select_related('user').all()
        return common_query.filter(Q() if user.is_staff else Q(user=user))
    
    @action(detail=False, methods=['get', 'patch'])
    def current_customer(self, request):
        customer = Customer.objects.select_related('user').get(user=request.user)
        if request.method == 'GET':
            serializer = SimpleCustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = SimpleCustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        
class CollectionViewset(ModelViewSet):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.all().annotate(products_count=Count('products'))
    permission_classes = [IsAdminOrReadOnly]

class ProductViewset(ModelViewSet):
    def get_serializer_class(self): 
        method = self.request.method
        if method not in SAFE_METHODS:
            return AddProductSerializer
        return ProductSerializer
    queryset = Product.objects.select_related('collection').all()
    permission_classes = [IsAdminOrReadOnly]

class CartViewset(RetrieveModelMixin,CreateModelMixin,GenericViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.select_related('customer__user').prefetch_related('items__product').all()
    def get_serializer_context(self):
        return {'user_id':self.request.user.id}
    permission_classes = [AllowUnauthenticatedForCart]
    
    @action(detail=True, methods=['post'])
    def merge_carts(self, request,pk):
        if request.method == 'POST':
            cart = Cart.objects.only('id').get(customer__user=request.user.id)
            serializer = MergeAnonymousCartSerializer(cart,data=request.data,context={'auth_cart_id':cart.id,'anon_cart_id':pk})
            serializer.is_valid(raise_exception=True)
            merge_cart = serializer.save()
            serializer = CartSerializer(merge_cart)
            return Response(serializer.data)

class CartItemViewset(ModelViewSet):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method in ['PATCH','PUT']:
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_queryset(self):
        return CartItem.objects.prefetch_related('cart').filter(cart_id=self.kwargs['cart_pk'])

    def create(self, request, *args, **kwargs):
        cart_item = CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])
        if request.method =='POST':
            serializer = AddCartItemSerializer(cart_item,data=request.data,context={'cart_id':self.kwargs['cart_pk']})
            serializer.is_valid(raise_exception=True)
            cart_item = serializer.save()
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)

class OrderViewset(ListModelMixin,RetrieveModelMixin,CreateModelMixin,UpdateModelMixin,GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated,StaffUpdatePermission]
    def check_permissions(self, request):
        return super().check_permissions(request)
    def get_queryset(self):
        user = self.request.user
        common_query = Order.objects.select_related('customer__user').prefetch_related('items__product')
        queryset = common_query.filter(
            Q() if user.is_staff else Q(customer__user=user)
        )
        return queryset  
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            serializer = OrderSerializer(data=request.data,context={'user_id':request.user.id})
            serializer.is_valid(raise_exception=True)
            order = serializer.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data)