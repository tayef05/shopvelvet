from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

from tags import views

router = DefaultRouter()
router.register('tag',views.TagViewset)

tag_router = NestedDefaultRouter(router,'tag',lookup='tag')
tag_router.register('items',views.TaggedItemViewset,basename='tagged_item')

urlpatterns = router.urls + tag_router.urls
