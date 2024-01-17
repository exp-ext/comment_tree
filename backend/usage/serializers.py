from rest_framework import serializers

from usage.models import Comment, Post


class BlankSerializer(serializers.Serializer):
    pass


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True, default=serializers.CurrentUserDefault())
    post = serializers.SlugRelatedField(slug_field='id', read_only=True)
    # parent_node = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, label='Родительская нода')
    parent_node = serializers.IntegerField(required=False, label='Родительская нода')
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'post', 'user', 'text', 'rating', 'parent_node')
