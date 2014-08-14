from cyder.cydns.txt.models import TXT
from cyder.api.v1.tests.base import APITests


class TXTAPI_Test(APITests):
    __test__ = True
    model = TXT

    def create_data(self):
        data = {
            'ctnr': self.ctnr,
            'label': 'txt',
            'domain': self.domain,
            'txt_data': 'Things',
        }
        obj, _ = self.model.objects.get_or_create(**data)
        return obj
