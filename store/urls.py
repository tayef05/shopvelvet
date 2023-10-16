from django.urls import path
# from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from store import views

router = DefaultRouter()

router.register('customers',views.CustomerViewset,basename='customer')
router.register('addresses',views.AddressViewset,basename='address')
router.register('collections',views.CollectionViewset)
router.register('products',views.ProductViewset)
router.register('orders',views.OrderViewset,basename='order')


router.register('carts',views.CartViewset)
cart_router = NestedDefaultRouter(router,'carts',lookup='cart')
cart_router.register('items',views.CartItemViewset,basename='cartitem')


urlpatterns = router.urls + cart_router.urls 
