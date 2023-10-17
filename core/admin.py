from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline

from core.models import User
from likes.models import LikedItem
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem

# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
         (('Personal info'), {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email')
            }),
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

class LikedItemInline(GenericTabularInline):
    model = LikedItem
    extra = 1

class TaggedItemInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem
    extra = 1

class CustomProductAdmin(ProductAdmin):
    inlines = [LikedItemInline,TaggedItemInline]

admin.site.unregister(Product)
admin.site.register(Product,CustomProductAdmin)