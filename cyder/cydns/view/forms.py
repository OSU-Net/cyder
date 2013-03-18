from cyder.cydns.forms import DNSForm
from cyder.cydns.view.models import View


class ViewForm(DNSForm):
    class Meta:
        model = View
