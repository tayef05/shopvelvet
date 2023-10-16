from django.contrib import admin
from django.urls import include, path

admin.site.site_header = 'Shopvelvet Admin'
admin.site.site_title = 'Shopvelvet Admin'
admin.site.index_title = 'Admin'
urlpatterns = [
    path("__debug__/", include("debug_toolbar.urls")),
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('store/',include('store.urls')),
]
