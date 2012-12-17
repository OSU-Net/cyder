from django.forms import ModelForm

from cyder.core.system.models import System


class SystemForm(ModelForm):
    class Meta:
        model = System
