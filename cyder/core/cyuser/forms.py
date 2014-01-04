from django import forms


class UserPermForm(forms.Form):
    users = forms.CharField(
        label="Users",
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}), required=True)
