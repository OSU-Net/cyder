from cyder.cydns.address_record.models import AddressRecord
from cyder.api.v1.tests.base import APITests


class AddressRecordBase(APITests):
    model = AddressRecord
    root = "dns"

    def create_data(self, label):
        return {
            'ctnr': self.ctnr,
            'description': 'Address Record',
            'ttl': 420,
            'label': label,
            'domain': self.domain,
        }


class AddressRecordv4API_Test(AddressRecordBase):
    __test__ = True

    def create_data(self):
        data = super(AddressRecordv4API_Test, self).create_data('foo')
        data.update({
            'ip_str': '11.193.4.12',
            'ip_type': '4',
        })
        obj, _ = self.model.objects.get_or_create(**data)
        obj.views.add(self.view.id)
        return obj


class AddressRecordv6API_Test(AddressRecordBase):
    __test__ = True

    def create_data(self):
        data = super(AddressRecordv6API_Test, self).create_data('bar')
        data.update({
            'ip_str': '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
            'ip_type': '6',
        })
        obj, _ = self.model.objects.get_or_create(**data)
        obj.views.add(self.view.id)
        return obj
