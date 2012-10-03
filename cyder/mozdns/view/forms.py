from django.forms import ModelForm

from cyder.mozdns.view.models import View


class ViewForm(ModelForm):
    class Meta:
        model = View
