from rest_framework import serializers

from cyder.api.v1.endpoints.api import CommonAPINestedAVSerializer
from cyder.api.v1.endpoints.dhcp import api
from cyder.cydhcp.site.models import Site, SiteAV


class SiteAVSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.Field(source='id')
    site = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-site-detail')
    attribute = serializers.SlugRelatedField(slug_field='name')

    class Meta:
        model = SiteAV


class SiteAVViewSet(api.CommonDHCPViewSet):
    model = SiteAV
    serializer_class = SiteAVSerializer


class SiteNestedKeyValueSerializer(CommonAPINestedAVSerializer):
    id = serializers.HyperlinkedIdentityField(
        view_name='api-dhcp-site_attributes-detail')

    class Meta:
        model = SiteAV
        fields = api.NestedAVFields


class SiteSerializer(api.CommonDHCPSerializer):
    parent = serializers.HyperlinkedRelatedField(
        read_only=True, view_name='api-dhcp-site-detail')
    siteav_set = SiteNestedKeyValueSerializer(many=True)

    class Meta(api.CommonDHCPMeta):
        model = Site


class SiteViewSet(api.CommonDHCPViewSet):
    model = Site
    serializer_class = SiteSerializer
