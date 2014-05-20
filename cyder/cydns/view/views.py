from cyder.cydns.view.models import View
from cyder.cydns.view.forms import ViewForm


class ViewView(object):
    model = View
    form_class = ViewForm
    queryset = View.objects.all()
