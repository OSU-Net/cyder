from django.core.exceptions import ValidationError
from django.forms.util import ErrorList, ErrorDict
from django.shortcuts import get_object_or_404, redirect, render

from cyder.cydhcp.keyvalue.utils import get_attrs, update_attrs
from cyder.cydhcp.views import (CydhcpCreateView, CydhcpDeleteView,
                                CydhcpListView)
from cyder.cydhcp.vlan.forms import VlanForm
from cyder.cydhcp.vlan.models import Vlan, VlanKeyValue


class VlanView(object):
    model = Vlan
    queryset = Vlan.objects.all()
    form_class = VlanForm


class VlanDeleteView(VlanView, CydhcpDeleteView):
    success_url = "/cydhcp/vlan/"


class VlanListView(VlanView, CydhcpListView):
    """ """


class VlanCreateView(VlanView, CydhcpCreateView):
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
