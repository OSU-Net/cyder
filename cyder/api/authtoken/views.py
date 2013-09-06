# from django.auth.contrib.models import User
from django import forms
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.shortcuts import render
from rest_framework.authtoken.views import ObtainAuthToken as _

from cyder.api.authtoken.models import Token


class ObtainAuthToken(_):
    pass


obtain_auth_token = ObtainAuthToken.as_view()


def token_detail(request, pk):
    token = Token.objects.get(pk=pk)
    user = token.user

    return render(request, 'authtoken/token_detail.html',
                  {'token': token, 'user': user})


class TokenRequestForm(forms.Form):
    purpose = forms.CharField(max_length=40)


def request_token(request):
    # prompt user for purpose, give them spiel about API access, then generate
    if request.method == 'POST':
        form = TokenRequestForm(request.POST)
        if form.is_valid():
            # create the new token
            token = Token.objects.create(
                user=request.user, purpose=form.cleaned_data['purpose'])
            # show the user their new token
            return HttpResponseRedirect(
                '/api/authtoken/{0}'.format(str(token.pk)))
    else:
        form = TokenRequestForm()
    return render(request, 'authtoken/request_token.html', {'form': form})


class TokenRevokeForm(forms.Form):
    pass


def revoke_token(request, pk):
    token = Token.objects.get(pk=pk)

    if not (request.user.is_superuser or request.user == token.user):
        return HttpResponseForbidden()

    # ask for confirmation, then revoke the key
    if request.method == 'POST':
        form = TokenRevokeForm(request.POST)
        if form.is_valid():
            token.delete()
            return render(request, 'authtoken/revoke_token_done.html')
        else:
            return HttpResponseBadRequest("Invalid form submission.")
    else:
        form = TokenRevokeForm()
        return render(request, 'authtoken/revoke_token.html',
                      {'form': form, 'token': token})
