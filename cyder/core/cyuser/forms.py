from django import forms


class UserPermForm(forms.Form):
    users = forms.CharField(label="Users", required=True)
