# Create your views here.
from cyder.mozdns.views import MozdnsDeleteView
from cyder.mozdns.views import MozdnsCreateView
from cyder.mozdns.views import MozdnsDetailView
from cyder.mozdns.views import MozdnsUpdateView
from cyder.mozdns.views import MozdnsListView
from cyder.mozdns.view.models import View
from cyder.mozdns.view.forms import ViewForm


class ViewView(object):
    model = View
    form_class = ViewForm
    queryset = View.objects.all()


class ViewDeleteView(ViewView, MozdnsDeleteView):
    """ """


class ViewDetailView(ViewView, MozdnsDetailView):
    """ """
    template_name = 'view/view_detail.html'


class ViewCreateView(ViewView, MozdnsCreateView):
    """ """


class ViewUpdateView(ViewView, MozdnsUpdateView):
    """ """


class ViewListView(ViewView, MozdnsListView):
    """ """
