from django.db import models
from django.db.models import Q
from django.db.models.loading import get_model

from cyder.base.eav.constants import ATTRIBUTE_INVENTORY
from cyder.base.eav.fields import EAVAttributeField
from cyder.base.eav.models import Attribute, EAVBase
from cyder.base.mixins import ObjectUrlMixin
from cyder.base.models import BaseModel
from cyder.base.utils import transaction_atomic
from cyder.core.system.validators import validate_no_spaces


class System(BaseModel, ObjectUrlMixin):
    name = models.CharField(
        max_length=255, unique=False, null=False, blank=False,
        validators=[validate_no_spaces])

    search_fields = ('name',)
    sort_fields = ('name',)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'cyder'
        db_table = 'system'

    @staticmethod
    def filter_by_ctnr(ctnr, objects=None):
        objects = objects or System.objects
        DynamicInterface = get_model('cyder', 'dynamicinterface')
        StaticInterface = get_model('cyder', 'staticinterface')
        dynamic_query = DynamicInterface.objects.filter(
            ctnr=ctnr).values_list('system')
        static_query = StaticInterface.objects.filter(
            ctnr=ctnr).values_list('system')
        return objects.filter(Q(id__in=static_query) | Q(id__in=dynamic_query))

    def check_in_ctnr(self, ctnr):
        return (self.staticinterface_set.filter(ctnr=ctnr).exists() or
                self.dynamicinterface_set.filter(ctnr=ctnr).exists())

    def details(self):
        """For tables."""
        data = super(System, self).details()
        data['data'] = [
            ('Name', 'name', self),
        ]
        return data

    @transaction_atomic
    def delete(self, *args, **kwargs):
        DynamicInterface = get_model('cyder', 'dynamicinterface')
        for interface in DynamicInterface.objects.filter(system=self):
            interface.delete(delete_system=False, commit=False)
        StaticInterface = get_model('cyder', 'staticinterface')
        for interface in StaticInterface.objects.filter(system=self):
            interface.delete(delete_system=False, commit=False)
        super(System, self).delete(*args, **kwargs)

    @staticmethod
    def eg_metadata():
        """EditableGrid metadata."""
        return {'metadata': [
            {'name': 'name', 'datatype': 'string', 'editable': True},
        ]}

    @transaction_atomic
    def save(self, *args, **kwargs):
        self.full_clean()

        super(System, self).save(*args, **kwargs)


class SystemAV(EAVBase):
    class Meta(EAVBase.Meta):
        app_label = 'cyder'
        db_table = 'system_av'

    entity = models.ForeignKey(System)
    attribute = EAVAttributeField(Attribute,
        type_choices=(ATTRIBUTE_INVENTORY,))
