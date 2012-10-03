from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from cyder.mozdns.master_form.views import mozdns_record
from cyder.mozdns.api.v1.api import v1_dns_api


urlpatterns = patterns('',
                       url(r'^$', mozdns_record, name='mozdns-index'),
                       url(r'^record/', include('cyder.mozdns.master_form.urls')),
                       url(r'^address_record/',
                           include ('cyder.mozdns.address_record.urls')),
                       url(r'^cname/', include('cyder.mozdns.cname.urls')),
                       url(r'^domain/', include('cyder.mozdns.domain.urls')),
                       url(r'^mx/', include('cyder.mozdns.mx.urls')),
                       url(r'^nameserver/', include('cyder.mozdns.nameserver.urls')),
                       url(r'^ptr/', include('cyder.mozdns.ptr.urls')),
                       url(r'^soa/', include('cyder.mozdns.soa.urls')),
                       url(r'^srv/', include('cyder.mozdns.srv.urls')),
                       url(r'^txt/', include('cyder.mozdns.txt.urls')),
                       url(r'^sshfp/', include('cyder.mozdns.sshfp.urls')),
                       url(r'^view/', include('cyder.mozdns.view.urls')),
                       url(r'^bind/', include('cyder.mozdns.mozbind.urls')),
                       url(r'^api/', include(v1_dns_api.urls)),

                       )
