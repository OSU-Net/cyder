from django.core.exceptions import ValidationError, ObjectDoesNotExist
from rest_framework import serializers, viewsets

from cyder.core.system.models import System
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


class CommonDNSSerializer(serializers.HyperlinkedModelSerializer):
    comment = serializers.CharField()
    domain = serializers.CharField()
    views = serializers.PrimaryKeyRelatedField(many=True)


class CommonDNSViewSet(viewsets.ModelViewSet):
    def list(self, request):
        return super(CommonDNSViewSet, self).list(self, request)

    def create(self, request):
        return super(CommonDNSViewSet, self).create(self, request)

    def retrieve(self, request, pk=None):
        return super(CommonDNSViewSet, self).retrieve(self, request)

    def update(self, request, pk=None):
        return super(CommonDNSViewSet, self).update(self, request)

    def partial_update(self, request, pk=None):
        return super(CommonDNSViewSet, self).partial_update(self, request)

    def destroy(self, request, pk=None):
        return super(CommonDNSViewSet, self).partial_update(self, request)


class DomainSerializer(CommonDNSSerializer):
    class Meta:
        model = Domain
        fields = ['name', 'master_domain', 'soa', 'is_reverse', 'dirty',
                'purgeable', 'delegated']


class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class CNAMESerializer(CommonDNSSerializer, FQDNMixin):
    class Meta:
        model = CNAME
        fields = standard_fields + CNAME.get_api_fields()


class CNAMEViewSet(viewsets.ModelViewSet):
    queryset = CNAME.objects.all()
    serializer_class = CNAMESerializer


class TXTSerializer(CommonDNSSerializer):
    class Meta:
        model = TXT
        fields = standard_fields + TXT.get_api_fields()


class TXTViewSet(viewsets.ModelViewSet):
    queryset = TXT.objects.all()
    serializer_class = TXTSerializer


class SRVSerializer(CommonDNSSerializer):
    class Meta:
        model = TXT
        fields = standard_fields + TXT.get_api_fields()


class SRVViewSet(viewsets.ModelViewSet):
    queryset = SRV.objects.all()
    serializer_class = SRVSerializer


class MXSerializer(CommonDNSSerializer):
    class Meta:
        model = MX
        fields = standard_fields + MX.get_api_fields()


class MXViewSet(viewsets.ModelViewSet):
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
        models = PTR
        fields = standard_fields + PTR.get_api_fields()


class PTRViewSet(viewsets.ModelViewSet):
    queryset = PTR.objects.all()
    serializer_class = PTRSerializer


class SystemSerializer(CommonDNSSerializer):
    class Meta:
        models = System
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
        super(StaticInterfaceViewSet, self).create(request)

    def update(self, request, pk=None):
        super(StaticInterfaceViewSet, self).update(request, pk)

    def partial_update(self, request, pk=None):
        super(StaticInterfaceViewSet, self).partial_update(request, pk)
