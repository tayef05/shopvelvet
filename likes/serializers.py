
from rest_framework import serializers

from likes.models import LikedItem


class LikedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikedItem
        fields = ['id','object_id','content_type','user_id']
    
    def create(self, validated_data):
        user_id = self.context['user_id']
        object_id = validated_data['object_id']
        (self.instance, created) = LikedItem.objects.get_or_create(user_id=user_id,**validated_data)
        if not created:
            raise serializers.ValidationError({'error':f"You have already liked this object with ID {object_id}. You cannot like it again."})
        return self.instance