from cyder.cydns.address_record.models import AddressRecord
from cyder.api.v1.tests.base import APITests


class AddressRecordv4API_Test(APITests):
    __test__ = True
    model = AddressRecord

    def create_data(self):
        obj = AddressRecord.objects.create(
            ctnr=self.ctnr, description='Address Record', ttl=420, label='foo',
            domain=self.domain, ip_str='11.193.4.12', ip_type='4'
        )
        obj.views.add(self.view)
        return obj


class AddressRecordv6API_Test(APITests):
    __test__ = True
    model = AddressRecord

    def create_data(self):
        obj = AddressRecord.objects.create(
            ctnr=self.ctnr, description='Address Record', ttl=420, label='foo',
            domain=self.domain,
            ip_str='2001:0db8:85a3:0000:0000:8a2e:0370:7334', ip_type='6'
        )
        obj.views.add(self.view)
        return obj
