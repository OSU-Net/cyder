from rest_framework import serializers, viewsets

from cyder.api.v1.endpoints.api import (CommonAPINestedAVSerializer,
                                        CommonAPIViewSet)
from cyder.core.system.models import System, SystemAV


class SystemAVSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='id')
    entity = serializers.HyperlinkedRelatedField(
        view_name='api-core-system-detail')
    attribute = serializers.SlugRelatedField(slug_field='name')

    class Meta:
        model = SystemAV


class SystemAVViewSet(viewsets.ModelViewSet):
    model = SystemAV
    queryset = SystemAV.objects.all()
    serializer_class = SystemAVSerializer


class SystemNestedAVSerializer(CommonAPINestedAVSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-core-system_attributes-detail')
    attribute = serializers.SlugRelatedField(slug_field='name')

    class Meta:
        model = SystemAV
        fields = ['id', 'attribute', 'value']


class SystemSerializer(serializers.ModelSerializer):
    systemav_set = SystemNestedAVSerializer(many=True)

    class Meta:
        model = System


class SystemViewSet(CommonAPIViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    avmodel = SystemAV
