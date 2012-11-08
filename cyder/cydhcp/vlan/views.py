from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.contrib import messages
from django.forms.util import ErrorList
from django.http import HttpResponse

from cyder.cydhcp.vlan.models import Vlan, VlanKeyValue
from cyder.cydhcp.vlan.forms import VlanForm
from cyder.cydhcp.network.models import Network
from cyder.cydhcp.site.models import Site
from cyder.cydhcp.keyvalue.utils import get_attrs, update_attrs

from cyder.cydhcp.views import CoreDeleteView, CoreListView
from cyder.cydhcp.views import CoreCreateView

import re
import pdb
import ipaddr


class VlanView(object):
    model = Vlan
    queryset = Vlan.objects.all()
    form_class = VlanForm


is_attr = re.compile("^attr_\d+$")


class VlanDeleteView(VlanView, CoreDeleteView):
    success_url = "/cydhcp/vlan/"


class VlanListView(VlanView, CoreListView):
    """ """
    template_name = "vlan/vlan_list.html"


class VlanCreateView(VlanView, CoreCreateView):
    """ """
    template_name = "cydhcp/cydhcp_form.html"


def update_vlan(request, vlan_pk):
    vlan = get_object_or_404(Vlan, pk=vlan_pk)
    attrs = vlan.vlankeyvalue_set.all()
    aux_attrs = VlanKeyValue.aux_attrs
    if request.method == "POST":
        form = VlanForm(request.POST, instance=vlan)
        if form.is_valid():
            try:
                # Handle KV store.
                kv = get_attrs(request.POST)
                update_attrs(kv, attrs, VlanKeyValue, vlan, "vlan")

                vlan = form.save()
                vlan.save()
                return redirect(vlan)
            except ValidationError, e:
                if form._errors is None:
                    form._errors = ErrorDict()
                form._errors["__all__"] = ErrorList(e.messages)
                return render(request, "vlan/vlan_edit.html", {
                    "vlan": vlan,
                    "form": form,
                    "attrs": attrs,
                    "aux_attrs": aux_attrs
                })
    else:
        form = VlanForm(instance=vlan)
        return render(request, "vlan/vlan_edit.html", {
            "vlan": vlan,
            "form": form,
            "attrs": attrs,
            "aux_attrs": aux_attrs
        })


def vlan_detail(request, vlan_pk):
    vlan = get_object_or_404(Vlan, pk=vlan_pk)
    attrs = vlan.vlankeyvalue_set.all()
    return render(request, "vlan/vlan_detail.html", {
        "vlan": vlan,
        "attrs": attrs
    })
