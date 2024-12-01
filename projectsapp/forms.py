from django import forms
from django.forms.widgets import SelectDateWidget


class CreateProjectForm(forms.Form):
    name = forms.CharField(label="Project name", max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})

class CreateTaskForm(forms.Form):
    name = forms.CharField(label="Task name", max_length=100)
    end_date = forms.DateField(label="End date", required=False, widget=SelectDateWidget())
    users = forms.ChoiceField(
        label="Assign to user", choices=None
    )

    def __init__(self, users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["users"].choices = users
        self.fields["name"].widget.attrs.update({"class": "form-control"})

