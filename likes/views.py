from django.db.models import Q
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from likes.models import LikedItem

from .serializers import LikedItemSerializer

# Create your views here.

class LikedItemViewset(ModelViewSet):

    def get_queryset(self):
        user = self.request.user
        common_query = LikedItem.objects.select_related('user').filter()
        return common_query.filter(Q() if user.is_staff else Q(user_id=user.id))
    
    serializer_class = LikedItemSerializer
    
    def get_serializer_context(self):
        return {'user_id':self.request.user.id}