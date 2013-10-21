from rest_framework import serializers

from cyder.api.v1.endpoints import api


NestedKeyValueFields = api.NestedKeyValueFields


class CommonDHCPSerializer(api.CommonAPISerializer):
    id = serializers.Field(source='id')
    pass


class CommonDHCPMeta(api.CommonAPIMeta):
    pass


class CommonDHCPViewSet(api.CommonAPIViewSet):
    pass
