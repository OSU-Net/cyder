from django import forms


class BugReportForm(forms.Form):

    bug = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea)
