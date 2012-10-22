from django.db import models

from cyder.core.node.models import Node
from cyder.core.registration.models import BaseRegistration
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.ptr.models import PTR


class StaticRegistration(BaseRegistration):
    address_record  = models.OneToOneField(AddressRecord)
    ptr             = models.OneToOneField(PTR)
    node            = models.ForeignKey(Node, null=False)

    class Meta:
        db_table = 'static_registration'
