from rest_framework.viewsets import ModelViewSet

from store.permissions import IsAdminOrReadOnly
from tags.models import Tag, TaggedItem
from tags.serializers import TaggedItemSerializer, TagSerializer

# Create your views here.

class TagViewset(ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TagSerializer

class TaggedItemViewset(ModelViewSet):
    def get_queryset(self):
        return TaggedItem.objects.select_related('tag').filter(tag=self.kwargs['tag_pk'])
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = TaggedItemSerializer
    def get_serializer_context(self):
        return {'tag_id':self.kwargs['tag_pk']}
