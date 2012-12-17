import json

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.forms.util import ErrorList, ErrorDict
from django.http import HttpResponse

from cyder.cydhcp.network.forms import *
from cyder.cydhcp.network.models import Network, NetworkKeyValue
from cyder.cydhcp.network.utils import calc_networks
from cyder.cydhcp.keyvalue.utils import (get_attrs, update_attrs, get_dhcp_aa,
                                         get_dhcp_docstrings, dict_to_kv)
from cyder.cydhcp.views import CydhcpDeleteView, CydhcpListView


class NetworkView(object):
    model = Network
    queryset = Network.objects.select_related('site').all()
    form_class = NetworkForm


class NetworkDeleteView(NetworkView, CydhcpDeleteView):
    success_url = "/cydhcp/network/"


class NetworkListView(NetworkView, CydhcpListView):
    """"""
    template_name = 'network/network_list.html'

def delete_network_attr(request, attr_pk):
    """
    An view destined to be called by ajax to remove an attr.
    """
    attr = get_object_or_404(NetworkKeyValue, pk=attr_pk)
    attr.delete()
    return HttpResponse("Attribute Removed.")


def create_network(request):
    if request.method == 'POST':
        form = NetworkForm(request.POST)
        network = form.instance
        if form.is_valid():
            if network.site is None:
                parent = calc_parent(network)
                if parent:
                    network.site = parent.site
            network.save()
            return redirect(network)
        else:
            return render(request, 'cydhcp/cydhcp_form.html', {
                'form': form,
        })

    else:
        form = NetworkForm()
        return render(request, 'cydhcp/cydhcp_form.html', {
            'form': form,
        })


def update_network(request, network_pk):
    network = get_object_or_404(Network, pk=network_pk)
    attrs = network.networkkeyvalue_set.all()
    docs = get_dhcp_docstrings(NetworkKeyValue())
    aa = get_dhcp_aa(NetworkKeyValue())
    if request.method == 'POST':
        form = NetworkForm(request.POST, instance=network)
        try:
            if not form.is_valid():
                return render(request, 'network/network_edit.html', {
                    'network': network,
                    'form': form,
                    'attrs': attrs,
                    'docs': docs,
                    'aa': json.dumps(aa)
                })
            else:
                # Handle key value stuff.
                kv = None
                kv = get_attrs(request.POST)
                update_attrs(kv, attrs, NetworkKeyValue, network, 'network')
                network = form.save()
                return redirect(network.get_update_url())
        except ValidationError, e:
            if form._errors is None:
                form._errors = ErrorDict()
            form._errors['__all__'] = ErrorList(e.messages)
            if kv:
                attrs = dict_to_kv(kv, NetworkKeyValue)
            return render(request, 'network/network_edit.html', {
                'network': network,
                'form': form,
                'attrs': attrs,
                'docs': docs,
                'aa': json.dumps(aa)
            })

    else:
        form = NetworkForm(instance=network)
        return render(request, 'network/network_edit.html', {
            'network': network,
            'form': form,
            'attrs': attrs,
            'docs': docs,
            'aa': json.dumps(aa)
        })


def network_detail(request, network_pk):
    network = get_object_or_404(Network, pk=network_pk)
    network.update_network()
    attrs = network.networkkeyvalue_set.all()
    eldars, sub_networks = calc_networks(network)
    ranges = network.range_set.all()
    return render(request, 'network/network_detail.html', {
        'network': network,
        'ranges': ranges,
        'eldars': eldars,
        'sub_networks': sub_networks,
        'attrs': attrs,
    })
