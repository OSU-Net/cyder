from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from django_cas.models import SessionServiceTicket
import requests

from cyder.core.ctnr.models import Ctnr
from cyder.core.cyuser.views import login_session


def get_saml_assertion(ticket):
    return """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Header/><SOAP-ENV:Body><samlp:Request xmlns:samlp="urn:oasis:names:tc:SAML:1.0:protocol"  MajorVersion="1" MinorVersion="1" RequestID="_192.168.16.51.1024506224022" IssueInstant="2002-06-19T17:03:44.022Z"><samlp:AssertionArtifact>%s</samlp:AssertionArtifact></samlp:Request></SOAP-ENV:Body></SOAP-ENV:Envelope>""" % ticket


class AuthenticationMiddleware(object):

    def process_request(self, request):
        if request.user.is_authenticated() and not request.user.is_anonymous():
            pass
        elif request.path in (reverse('login'), reverse('logout')):
            return
        else:
            return redirect(reverse('login'))

        if not 'ctnr' in request.session:
            request = login_session(request, request.user.username)

        if not request.user.email:
            # Get user attributes from CAS via SAML.
            ticket = SessionServiceTicket.objects.get(
                session_key=request.session.session_key).service_ticket

            url = 'https://cyder.nws.oregonstate.edu'
            headers = {
                'soapaction': 'http://www.oasis-open.org/committees/security',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'accept': 'text/xml',
                'connection': 'keep-alive',
                'content-type': 'text/xml'
            }
            res = requests.post(
                'https://login.oregonstate.edu/cas/samlValidate?TARGET=%s' % url,
                data=get_saml_assertion(ticket), headers=headers),

            # from django.http import HttpResponse
            # import cgi
            # return HttpResponse(str(res[0].text))
