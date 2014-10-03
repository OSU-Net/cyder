from cyder.cydns.cname.models import CNAME
from cyder.api.v1.tests.base import APITests


class CNAMEAPI_Test(APITests):
    __test__ = True
    model = CNAME

    def create_data(self):
        data = {
            'ctnr': self.ctnr,
            'description': 'CNAME record',
            'ttl': 420,
            'label': 'baz',
            'domain': self.domain,
            'target': 'bar.' + self.domain.name,
        }
        obj, _ = self.model.objects.get_or_create(**data)
        obj.views.add(self.view.id)
        return obj
