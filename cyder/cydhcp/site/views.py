from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.forms.util import ErrorList, ErrorDict

from cyder.cydhcp.site.models import Site, SiteKeyValue
from cyder.cydhcp.site.forms import SiteForm
from cyder.cydhcp.site.utils import get_vlans

from cyder.cydhcp.network.models import Network
from cyder.cydhcp.keyvalue.utils import get_attrs, update_attrs

from cyder.cydhcp.views import CydhcpDeleteView, CydhcpListView
from cyder.cydhcp.views import CydhcpCreateView, CydhcpUpdateView

import re


class SiteView(object):
    model = Site
    queryset = Site.objects.all()
    form_class = SiteForm


is_attr = re.compile("^attr_\d+$")


class SiteDeleteView(SiteView, CydhcpDeleteView):
    success_url = "/cydhcp/site/"


def delete_site(request, site_pk):
    get_object_or_404(Site, pk=site_pk)
    return render(request, "site/site_confirm_delete.html")


class SiteListView(SiteView, CydhcpListView):
    """"""
    template_name = "cydhcp/cydhcp_list.html"


class SiteCreateView(SiteView, CydhcpCreateView):
    """"""
    template_name = "cydhcp/cydhcp_form.html"


class SiteUpdateView(SiteView, CydhcpUpdateView):
    """"""
    template_name = "site/site_edit.html"


def update_site(request, site_pk):
    site = get_object_or_404(Site, pk=site_pk)
    attrs = site.sitekeyvalue_set.all()
    aux_attrs = SiteKeyValue.aux_attrs
    if request.method == "POST":
        form = SiteForm(request.POST, instance=site)
        try:
            if form.is_valid():
                # Handle KV store.
                kv = get_attrs(request.POST)
                update_attrs(kv, attrs, SiteKeyValue, site, "site")
                site = form.save()

            return redirect(site)
        except ValidationError, e:
            if form._errors is None:
                form._errors = ErrorDict()
            form._errors["__all__"] = ErrorList(e.messages)
            return render(request, "site/site_edit.html", {
                "site": site,
                "form": form,
                "attrs": attrs,
                "aux_attrs": aux_attrs
            })
    else:
        form = SiteForm(instance=site)
        return render(request, "site/site_edit.html", {
            "site": site,
            "form": form,
            "attrs": attrs,
            "aux_attrs": aux_attrs
        })


def site_detail(request, site_pk):
    site = get_object_or_404(Site, pk=site_pk)
    attrs = site.sitekeyvalue_set.all()
    child_sites = site.site_set.all()
    networks = Network.objects.filter(site=site)
    paginator = Paginator(networks, 20)
    page = request.GET.get('page')
    try:
        networks = paginator.page(page)
    except PageNotAnInteger:
        networks = paginator.page(1)
    except EmptyPage:
        networks = paginator.page(paginator.num_pages)
    return render(request, "site/site_detail.html", {
        "site": site,
        "networks": networks,
        "child_sites": child_sites,
        "attrs": attrs,
    })
