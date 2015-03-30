from django import forms
from django.core.exceptions import ValidationError

from cyder.models import Ctnr
from cyder.cydns.address_record.models import AddressRecord
from cyder.cydns.forms import DNSForm
from cyder.cydns.nameserver.models import Nameserver
from cyder.cydhcp.interface.static_intr.models import StaticInterface
from cyder.base.mixins import UsabilityFormMixin


class NameserverForm(DNSForm, UsabilityFormMixin):
    glue_ip_str = forms.CharField(label="Glue's IP Address", required=False)
    glue_ctnr = forms.ModelChoiceField(
        queryset=Ctnr.objects.all(),
        required=False,
        label="Glue's Container")

    class Meta:
        model = Nameserver
        fields = ('domain', 'server', 'views', 'ttl', 'glue_ip_str',
                  'glue_ctnr', 'description')
        exclude = ('addr_glue', 'intr_glue')
        widgets = {'views': forms.CheckboxSelectMultiple}

    def __init__(self, *args, **kwargs):
        super(NameserverForm, self).__init__(*args, **kwargs)
        if not self.instance:
            return
        if not self.instance.glue:
            # If it doesn't have glue, it doesn't need it.
            return
        addr_glue = AddressRecord.objects.filter(
            label=self.instance.glue.label,
            domain=self.instance.glue.domain)
        intr_glue = StaticInterface.objects.filter(
            label=self.instance.glue.label,
            domain=self.instance.glue.domain)

        glue_choices = []
        for glue in addr_glue:
            glue_choices.append(("addr_{0}".format(glue.pk), str(glue)))
        for glue in intr_glue:
            glue_choices.append(("intr_{0}".format(glue.pk), str(glue)))

        if isinstance(self.instance.glue, AddressRecord):
            initial = "addr_{0}".format(self.instance.glue.pk)
        elif isinstance(self.instance.glue, StaticInterface):
            initial = "intr_{0}".format(self.instance.glue.pk)

        self.fields['glue'] = forms.ChoiceField(choices=glue_choices,
                                                initial=initial)

    def clean(self, *args, **kwargs):
        self.glue = None
        if self.instance.pk is None:
            domain = self.cleaned_data['domain']
            glue_ip_str, glue_ctnr = (self.cleaned_data['glue_ip_str'],
                                      self.cleaned_data['glue_ctnr'])
            server = self.cleaned_data['server']
            if '.' in server:
                glue_label, glue_domain = tuple(server.split('.', 1))
                glue_domain = glue_domain.strip('.').lower()
            else:
                glue_label, glue_domain = None, None
            if domain.delegated:
                if glue_domain and glue_domain != domain.name.lower():
                    if glue_ip_str or glue_ctnr:
                        raise ValidationError(
                            "This record does not need glue, so "
                            "please leave the glue fields blank.")
                else:
                    if not (glue_ip_str and glue_ctnr):
                        raise ValidationError(
                            "This zone is delegated, so "
                            "please provide information for glue.")
                    self.glue = AddressRecord(domain=domain, label=glue_label,
                                              ip_str=glue_ip_str,
                                              ctnr=glue_ctnr)
                    self.glue.set_is_glue()
                    self.glue.save()
            elif not domain.delegated and (glue_ip_str or glue_ctnr):
                raise ValidationError("This zone is not delegated, so please "
                                      "leave the glue fields blank.")
        cleaned_data = super(NameserverForm, self).clean(*args, **kwargs)
        return cleaned_data

    def save(self, *args, **kwargs):
        try:
            super(NameserverForm, self).save(*args, **kwargs)
        except ValidationError, e:
            if self.glue is not None:
                self.glue.delete()
            raise e


class NSDelegated(forms.Form):
    server = forms.CharField()
    server_ip_address = forms.CharField()
