from rest_framework.routers import DefaultRouter

from likes import views

router = DefaultRouter()
router.register('likes',views.LikedItemViewset,basename='like')

urlpatterns = router.urls