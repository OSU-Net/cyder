from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render

from cyder.cydns.views import CydnsCreateView
from cyder.cydns.views import CydnsDeleteView
from cyder.cydns.views import CydnsDetailView
from cyder.cydns.views import CydnsListView
from cyder.cydns.views import CydnsUpdateView
from cyder.cydns.ip.forms import IpForm
from cyder.cydns.ptr.forms import PTRForm
from cyder.cydns.ptr.models import PTR
from cyder.cydns.domain.models import Domain
from cyder.cydhcp.network.utils import calc_parent_str


class PTRView(object):
    model = PTR
    form_class = PTRForm
    queryset = PTR.objects.all()


class PTRDeleteView(PTRView, CydnsDeleteView):
    """ """


class PTRDetailView(PTRView, CydnsDetailView):
    """ """
    template_name = "ptr/ptr_detail.html"


class PTRCreateView(PTRView, CydnsCreateView):
    def get_form(self, *args, **kwargs):
        initial = self.get_form_kwargs()
        if 'ip_type' in self.request.GET and 'ip_str' in self.request.GET:
            ip_str = self.request.GET['ip_str']
            ip_type = self.request.GET['ip_type']
            network = calc_parent_str(ip_str, ip_type)
            if network and network.vlan and network.site:
                expected_name = "{0}.{1}.mozilla.com".format(network.vlan.name,
                                                             network.site.get_site_path())
                try:
                    domain = Domain.objects.get(name=expected_name)
                except ObjectDoesNotExist, e:
                    domain = None

            if domain:
                initial['initial'] = {'ip_str': ip_str,
                                      'name': "." + domain.name, 'ip_type': ip_type}
            else:
                initial['initial'] = {'ip_str': ip_str, 'ip_type': ip_type}

        return PTRForm(**initial)


class PTRUpdateView(PTRView, CydnsUpdateView):
    """ """


class PTRListView(PTRView, CydnsListView):
    """ """
