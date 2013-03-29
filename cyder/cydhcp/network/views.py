from cyder.base.utils import tablefy
from cyder.cydhcp.network.forms import *
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.network.utils import calc_networks
from cyder.cydhcp.views import CydhcpDetailView


class NetworkView(object):
    model = Network
    form_class = NetworkForm
    queryset = Network.objects.all()
    extra_context = {'obj_type': 'network'}


class NetworkDetailView(NetworkView, CydhcpDetailView):
    template_name = 'network/network_detail.html'

    def get_context_data(self, **kwargs):
        context = super(NetworkDetailView, self).get_context_data(**kwargs)
        network = kwargs.get('object', False)
        if not network:
            return network
        parent_networks, child_networks = calc_networks(network)
        context = dict({
            'network_table': tablefy((network,)),
            'ranges_table': tablefy(network.range_set.all()),
            'parent_network_table': tablefy(parent_networks),
            'sub_networks_table': tablefy(child_networks),
            'attrs_table': tablefy(network.networkkeyvalue_set.all()),
        }.items() + context.items())
        return context
