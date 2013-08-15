from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework import serializers, viewsets

from cyder.core.system.models import System, SystemKeyValue
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.cydhcp.interface.static_intr.models import StaticIntrKeyValue
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.cname.models import CNAME
from cyder.cydns.domain.models import Domain
from cyder.cydns.mx.models import MX
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydns.ptr.models import PTR
from cyder.cydns.srv.models import SRV
from cyder.cydns.sshfp.models import SSHFP
from cyder.cydns.txt.models import TXT
from cyder.cydns.utils import ensure_label_domain, prune_tree
from cyder.cydns.view.models import View


standard_fields = ['id']


class FQDNMixin(object):
    def restore_object(self, attrs, instance=None):
        if self.fqdn:
            try:
                self.label, self.domain = ensure_label_domain(self.fqdn)
            except ValidationError, e:
                self._errors['fqdn'] = e.messages


class ViewMixin(object):
    views = serializers.PrimaryKeyRelatedField(many=True)



class CommonDNSSerializer(serializers.HyperlinkedModelSerializer):
    comment = serializers.CharField()
    views = serializers.PrimaryKeyRelatedField(many=True)


class CommonDNSViewSet(viewsets.ModelViewSet):
    """
    def get_queryset(self):
        queryset = self.model.objects.all()
        query_kwargs = {
            key + '__iexact': value
            for (key, value)
            in self.request.QUERY_PARAMS
            if key in self.model.search_fields
        }

        if len(query_kwargs):
            queryset = queryset.filter(**query_kwargs)

        return queryset
    """


class DomainSerializer(serializers.HyperlinkedModelSerializer):
    master_domain = serializers.HyperlinkedRelatedField(
        many=False, read_only=True, view_name='domain-detail')

    class Meta:
        model = Domain
        fields = ['id', 'name', 'master_domain', 'soa', 'is_reverse', 'dirty',
                'purgeable', 'delegated']


class DomainViewSet(CommonDNSViewSet):
    model = Domain
    serializer_class = DomainSerializer


class CNAMESerializer(CommonDNSSerializer, FQDNMixin):
    class Meta:
        model = CNAME
        fields = standard_fields + CNAME.get_api_fields()


class CNAMEViewSet(CommonDNSViewSet):
    model = CNAME
    serializer_class = CNAMESerializer


class TXTSerializer(CommonDNSSerializer):
    class Meta:
        model = TXT
        fields = standard_fields + TXT.get_api_fields()


class TXTViewSet(CommonDNSViewSet):
    queryset = TXT.objects.all()
    serializer_class = TXTSerializer


class SRVSerializer(CommonDNSSerializer):
    class Meta:
        model = TXT
        fields = standard_fields + TXT.get_api_fields()


class SRVViewSet(CommonDNSViewSet):
    queryset = SRV.objects.all()
    serializer_class = SRVSerializer


class MXSerializer(CommonDNSSerializer):
    class Meta:
        model = MX
        fields = standard_fields + MX.get_api_fields()


class MXViewSet(CommonDNSViewSet):
    queryset = MX.objects.all()
    serializer_class = MXSerializer


class SSHFPSerializer(CommonDNSSerializer):
    class Meta:
        model = SSHFP
        fields = standard_fields + SSHFP.get_api_fields()


class SSHFPViewSet(viewsets.ModelViewSet):
    queryset = SSHFP.objects.all()
    serializer_class = SSHFPSerializer


class AddressRecordSerializer(CommonDNSSerializer):
    class Meta:
        model = AddressRecord
        fields = standard_fields + AddressRecord.get_api_fields()


class AddressRecordViewSet(viewsets.ModelViewSet):
    queryset = AddressRecord.objects.all()
    serializer_class = AddressRecordSerializer


class NameserverSerializer(CommonDNSSerializer):
    class Meta:
        models = Nameserver
        fields = standard_fields + Nameserver.get_api_fields()


class NameserverViewSet(viewsets.ModelViewSet):
    queryset = Nameserver.objects.all()
    serializer_class = NameserverSerializer


class PTRSerializer(CommonDNSSerializer):
    class Meta:
        model = PTR
        fields = standard_fields + PTR.get_api_fields()


class PTRViewSet(viewsets.ModelViewSet):
    queryset = PTR.objects.all()
    serializer_class = PTRSerializer


class SystemKeyValueSerializer(CommonDNSSerializer):
    system = serializers.HyperlinkedRelatedField(
            read_only=True, view_name="system")

    class Meta:
        model = SystemKeyValue


class SystemSerializer(CommonDNSSerializer):
    class Meta:
        model = System
        depth = 1


class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer


class StaticIntrKeyValueSerializer(CommonDNSSerializer):
    static_interface = serializers.HyperlinkedRelatedField(
        read_only=True, view_name="staticinterface")

    class Meta:
        model = StaticIntrKeyValue


class StaticInterfaceSerializer(CommonDNSSerializer):
    class Meta:
        model = StaticInterface
        fields = standard_fields + StaticInterface.get_api_fields() + ['system',
            'staticintrkeyvalue_set']
        depth = 1


class StaticInterfaceViewSet(viewsets.ModelViewSet):
    queryset = StaticInterface.objects.all()
    serializer_class = StaticInterfaceSerializer

    def create(self, request):
        # super(StaticInterfaceViewSet, self).create(request)
        pass

    def update(self, request, pk=None):
        # super(StaticInterfaceViewSet, self).update(request, pk)
        pass

    def partial_update(self, request, pk=None):
        # super(StaticInterfaceViewSet, self).partial_update(request, pk)
        pass

    def destroy(self, request, pk=None):
        pass
