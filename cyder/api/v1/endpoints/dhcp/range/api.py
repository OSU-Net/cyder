from rest_framework import serializers

from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.range.models import Range, RangeKeyValue


class RangeKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='id')
    range = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-range-detail')

    class Meta:
        model = RangeKeyValue


class RangeKeyValueViewSet(api.CommonDHCPViewSet):
    model = RangeKeyValue
    serializer_class = RangeKeyValueSerializer


class RangeNestedKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-range_keyvalues-detail')

    class Meta:
        model = RangeKeyValue
        fields = api.NestedKeyValueFields


class RangeSerializer(api.CommonDHCPSerializer):
    rangekeyvalue_set = RangeNestedKeyValueSerializer(many=True)

    class Meta(api.CommonDHCPMeta):
        model = Range
        depth = 1


class RangeViewSet(api.CommonDHCPViewSet):
    model = Range
    serializer_class = RangeSerializer
