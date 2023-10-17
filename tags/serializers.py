from rest_framework import serializers

from tags.models import Tag, TaggedItem


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id','label']

class TaggedItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TaggedItem
        fields = ['id', 'object_id', 'content_type']

    def create(self, validated_data):
        tag_id = self.context['tag_id']
        object_id = validated_data['object_id']
        content_type = validated_data['content_type']
        try:
            Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            raise serializers.ValidationError({'error':"Tag with the given ID does not exist."})
        (self.instance, created) = TaggedItem.objects.get_or_create(tag_id=tag_id, **validated_data)
        if not created:
            raise serializers.ValidationError({'error': f"A TaggedItem with tag ID {tag_id}, object ID {object_id}, and content type '{content_type}' already exists."})
        return self.instance