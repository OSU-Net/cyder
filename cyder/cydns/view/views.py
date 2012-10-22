# Create your views here.
from cyder.cydns.views import MozdnsDeleteView
from cyder.cydns.views import MozdnsCreateView
from cyder.cydns.views import MozdnsDetailView
from cyder.cydns.views import MozdnsUpdateView
from cyder.cydns.views import MozdnsListView
from cyder.cydns.view.models import View
from cyder.cydns.view.forms import ViewForm


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
