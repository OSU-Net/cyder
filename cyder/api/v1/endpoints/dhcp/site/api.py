from rest_framework import serializers

from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.site.models import Site, SiteKeyValue


class SiteKeyValueSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='id')
    site = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-site-detail')

    class Meta:
        model = SiteKeyValue


class SiteKeyValueViewSet(api.CommonDHCPViewSet):
    model = SiteKeyValue
    serializer_class = SiteKeyValueSerializer


class SiteNestedKeyValueSerializer(serializers.ModelSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-site_keyvalues-detail')

    class Meta:
        model = SiteKeyValue
        fields = api.NestedKeyValueFields


class SiteSerializer(api.CommonDHCPSerializer):
    parent = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-site-detail')
    sitekeyvalue_set = SiteNestedKeyValueSerializer(many=True)

    class Meta(api.CommonDHCPMeta):
        model = Site


class SiteViewSet(api.CommonDHCPViewSet):
    model = Site
    serializer_class = SiteSerializer
