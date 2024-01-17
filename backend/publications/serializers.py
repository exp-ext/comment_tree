from rest_framework import serializers


def create_comment_node_serializer(model_class):
    """
    Создает и возвращает класс сериализатора для моделей комментариев, наследуемых от AbstractComment.
    Эта фабричная функция динамически создает сериализатор для указанного класса модели комментария.

    ## Args:
    - model_class (class): Класс модели комментария, наследуемый от AbstractComment, для которого необходимо создать сериализатор.

    ## Returns:
    - class: Класс сериализатора, настроенного для работы с указанной моделью.

    ## Example:
        CommentNodeSerializer = create_comment_node_serializer(MyCommentModel)
        serializer = CommentNodeSerializer(instance=my_comment_instance)
        serialized_data = serializer.data
    """
    class DynamicCommentNodeSerializer(serializers.ModelSerializer):
        children = serializers.SerializerMethodField()

        class Meta:
            model = model_class
            exclude = ('path', 'numchild', 'inverted_rating')

        def get_children(self, obj):
            if obj.numchild == 0:
                return []
            return DynamicCommentNodeSerializer(obj.get_children(), many=True).data

    return DynamicCommentNodeSerializer


def create_post_comment_serializer(model_class):
    """
    Создает и возвращает класс сериализатора для моделей, наследуемых от AbstractPost.
    Эта фабричная функция динамически создает сериализатор для указанного класса модели.

    ## Args:
    - model_class (class): Класс модели, наследуемой от AbstractPost, для которой необходимо создать сериализатор.

    ## Returns:
    - class: Класс сериализатора, настроенного для работы с указанной моделью.

    ## Example:
        PostCommentSerializer = create_post_comment_serializer(MyPostModel)
        serializer = PostCommentSerializer(instance=my_post_instance)
        serialized_data = serializer.data
    """
    class DynamicPostCommentSerializer(serializers.ModelSerializer):
        comments = serializers.SerializerMethodField()

        class Meta:
            model = model_class
            fields = '__all__'

        def get_comments(self, obj):
            comments = obj.comments.filter(depth=1)
            comment_serializer_class = create_comment_node_serializer(obj.comments.model)
            return comment_serializer_class(comments, many=True).data

    return DynamicPostCommentSerializer
