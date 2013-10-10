from rest_framework import serializers, viewsets


NestedKeyValueFields = ['id', 'key', 'value', 'is_quoted']


class CommonAPISerializer(serializers.ModelSerializer):
    pass


class CommonAPIMeta:
    pass


class CommonAPIViewSet(viewsets.ModelViewSet):
    def __init__(self, *args, **kwargs):
        self.queryset = self.model.objects.all()
        super(CommonAPIViewSet, self).__init__(*args, **kwargs)
