import json
from django.contrib.auth.models import User

from cyder.api.v1.endpoints.core.tests import CoreAPITests
from cyder.core.ctnr.models import Ctnr


class CtnrAPI_Test(CoreAPITests):
    model = Ctnr

    def create_data(self):
        ctnr_data = {
            'name': 'ctnr',
        }
        ctnr, _ = self.model.objects.get_or_create(**ctnr_data)
        user_data = {
            'username': 'testuser',
        }
        user, _ = User.objects.get_or_create(**user_data)
        ctnr.users.add(user)
        
        return ctnr
