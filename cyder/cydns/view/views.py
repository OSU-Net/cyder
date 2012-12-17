# Create your views here.
from cyder.cydns.views import CydnsDeleteView
from cyder.cydns.views import CydnsCreateView
from cyder.cydns.views import CydnsDetailView
from cyder.cydns.views import CydnsUpdateView
from cyder.cydns.views import CydnsListView
from cyder.cydns.view.models import View
from cyder.cydns.view.forms import ViewForm


class ViewView(object):
    model = View
    form_class = ViewForm
    queryset = View.objects.all()


class ViewDeleteView(ViewView, CydnsDeleteView):
    """"""


class ViewDetailView(ViewView, CydnsDetailView):
    """"""
    template_name = 'view/view_detail.html'


class ViewCreateView(ViewView, CydnsCreateView):
    """"""


class ViewUpdateView(ViewView, CydnsUpdateView):
    """"""


class ViewListView(ViewView, CydnsListView):
    """"""
