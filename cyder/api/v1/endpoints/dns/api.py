from django.core.exceptions import ValidationError
from rest_framework import serializers

from cyder.api.v1.endpoints import api
from cyder.cydns.utils import ensure_label_domain


NestedKeyValueFields = api.NestedAVFields


class FQDNMixin(object):
    def restore_object(self, attrs):
        if self.fqdn:
            try:
                self.label, self.domain = ensure_label_domain(self.fqdn)
            except ValidationError, e:
                self._errors['fqdn'] = e.messages


class LabelDomainMixin(object):
    label = serializers.CharField()
    domain = serializers.HyperlinkedRelatedField(
        many=False, read_only=True, view_name='api-dns-domain-detail')


class CommonDNSSerializer(api.CommonAPISerializer):
    views = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name')


class CommonDNSMeta(api.CommonAPIMeta):
    pass


class CommonDNSViewSet(api.CommonAPIViewSet):
    pass
