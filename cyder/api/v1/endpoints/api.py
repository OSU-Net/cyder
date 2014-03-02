from rest_framework import serializers, viewsets


NestedAVFields = ['id', 'attribute', 'value']


class CommonAPISerializer(serializers.ModelSerializer):
    pass


class CommonAPINestedAVSerializer(serializers.ModelSerializer):
    attribute = serializers.SlugRelatedField(slug_field='name')


class CommonAPIMeta:
    pass


class CommonAPIViewSet(viewsets.ModelViewSet):
    def __init__(self, *args, **kwargs):
        self.queryset = self.model.objects.all()
        super(CommonAPIViewSet, self).__init__(*args, **kwargs)
