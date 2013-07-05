from django.forms import ModelForm

from cyder.cydns.domain.models import Domain
from cyder.cydns.soa.models import SOA


class DomainForm(ModelForm):
    class Meta:
        model = Domain
        exclude = ('master_domain', 'is_reverse', 'dirty', 'purgeable')

    def __init__(self, *args, **kwargs):
        super(DomainForm, self).__init__(*args, **kwargs)
        self.fields['soa'].queryset = SOA.objects.order_by("description")


class DomainUpdateForm(ModelForm):
    class Meta:
        model = Domain
        exclude = ('name', 'master_domain', 'purgeable')
