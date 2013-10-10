from rest_framework import serializers

from cyder.api.v1.endpoints.api import CommonAPINestedAVSerializer
from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.range.models import Range, RangeAV


class RangeAVSerializer(serializers.ModelSerializer):
    id = serializers.Field(source='id')
    range = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-range-detail')
    attribute = serializers.SlugRelatedField(slug_field='name')

    class Meta:
        model = RangeAV


class RangeAVViewSet(api.CommonDHCPViewSet):
    model = RangeAV
    serializer_class = RangeAVSerializer


class RangeNestedKeyValueSerializer(CommonAPINestedAVSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-range_attributes-detail')

    class Meta:
        model = RangeAV
        fields = api.NestedAVFields


class RangeSerializer(api.CommonDHCPSerializer):
    rangeav_set = RangeNestedKeyValueSerializer(many=True)

    class Meta(api.CommonDHCPMeta):
        model = Range
        depth = 1


class RangeViewSet(api.CommonDHCPViewSet):
    model = Range
    serializer_class = RangeSerializer
    avmodel = RangeAV
