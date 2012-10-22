from django.db import models

from cyder.core.ctnr.models import Ctnr
from cyder.core.registration.models import BaseRegistration


class DynamicRegistration(BaseRegistration):
    Ctnr            = models.ForeignKey(Ctnr, null=False)

    class Meta:
        db_table = 'dynamic_registration'
