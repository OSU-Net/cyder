from django.forms import ModelForm

from cyder.cydns.view.models import View


class ViewForm(ModelForm):
    class Meta:
        model = View
