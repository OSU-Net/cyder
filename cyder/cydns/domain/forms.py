from django.forms import ModelForm

from cyder.cydns.domain.models import Domain


class DomainForm(ModelForm):
    class Meta:
        model = Domain
        exclude = ('master_domain', 'is_reverse', 'dirty')


class DomainUpdateForm(ModelForm):
    class Meta:
        model = Domain
        exclude = ('name', 'master_domain',)
