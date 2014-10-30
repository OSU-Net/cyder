from django.forms import ModelForm

from cyder.cydns.domain.models import Domain
from cyder.base.mixins import UsabilityFormMixin


class DomainForm(ModelForm, UsabilityFormMixin):
    class Meta:
        model = Domain
        exclude = ('soa', 'master_domain', 'is_reverse', 'dirty', 'purgeable')


class DomainUpdateForm(ModelForm):
    class Meta:
        model = Domain
        exclude = ('soa', 'name', 'master_domain', 'purgeable')
