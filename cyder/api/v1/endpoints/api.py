from django.utils.decorators import classonlymethod
from django.views.decorators.csrf import csrf_exempt
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

    #@classonlymethod
    #@csrf_exempt
    #def as_view(cls, *args, **kwargs):
    #    super(CommonAPIViewSet, cls).as_view(*args, **kwargs)