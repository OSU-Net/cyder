from django import forms


class BugReportForm(forms.Form):

    bug = forms.CharField(label="Bug (required)", required=True)
    description = forms.CharField(
        label="Description (required)",
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}), required=True)
    reproduce = forms.CharField(
        label="How to reproduce the error",
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}), required=False)
    expected = forms.CharField(
        label="The expected result",
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}), required=False)
    actual = forms.CharField(
        label="The actual result",
        widget=forms.Textarea(attrs={'rows': 4, 'cols': 50}), required=False)
    session_data = forms.CharField(widget=forms.HiddenInput())


class EditUserForm(forms.Form):
    user = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'user-searchbox'}))
    action = forms.ChoiceField(
        widget=forms.RadioSelect, choices=(
            ('Promote', 'Promote to Superuser'),
            ('Demote', 'Demote from Superuser'),
            ('Create', 'Create a user'),
            ('Delete', 'Permanently delete user')))


def stripCharField(self, value):
    return charFieldClean(self, value.strip())


charFieldClean = forms.fields.CharField.clean
forms.fields.CharField.clean = stripCharField
