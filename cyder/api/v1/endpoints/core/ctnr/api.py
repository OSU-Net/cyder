from rest_framework import serializers
from rest_framework.reverse import reverse

from cyder.api.v1.endpoints.core import api
from cyder.core.ctnr.models import Ctnr


class CtnrSerializer(api.CommonCoreSerializer):
    users = serializers.SerializerMethodField('ctnrusers')
    domains = serializers.SerializerMethodField('ctnrdomains')
    ranges = serializers.SerializerMethodField('ctnrranges')
    workgroups = serializers.SerializerMethodField('ctnrworkgroups')

    def ctnrusers(self, obj):
        if obj is None:
            return
        return (reverse('api-core-user-list', request=self.context['request'])
                + "?ctnr_id=" + str(obj.id))

    def ctnrdomains(self, obj):
        if obj is None:
            return
        return (reverse('api-dns-domain-list', request=self.context['request'])
                + "?ctnr_id=" + str(obj.id))

    def ctnrranges(self, obj):
        if obj is None:
            return
        return (reverse('api-dhcp-range-list', request=self.context['request'])
                + "?ctnr_id=" + str(obj.id))

    def ctnrworkgroups(self, obj):
        if obj is None:
            return
        return (reverse('api-dhcp-workgroup-list',
                request=self.context['request'])
                + "?ctnr_id=" + str(obj.id))

    class Meta(api.CommonCoreMeta):
        model = Ctnr


class CtnrViewSet(api.CommonCoreViewSet):
    model = Ctnr
    serializer_class = CtnrSerializer
