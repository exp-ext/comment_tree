from rest_framework import serializers

from publications.models import Comment, Post


class BlankSerializer(serializers.Serializer):
    pass


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True, default=serializers.CurrentUserDefault())
    post = serializers.SlugRelatedField(slug_field='id', read_only=True)
    # parent_node = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, label='Родительская нода')
    parent_node = serializers.IntegerField(required=False, label='Родительская нода')

    class Meta:
        model = Comment
        fields = ('id', 'post', 'user', 'text', 'parent_node')


class CommentNodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'

    def get_children(self, obj):
        if obj.numchild == 0:
            return []
        return CommentNodeSerializer(obj.get_children(), many=True).data


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class PostCommentSerializer(PostSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'

    def get_comments(self, obj):
        comments = obj.comments.filter(depth=1)
        return CommentNodeSerializer(comments, many=True).data
