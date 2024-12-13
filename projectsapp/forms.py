from django import forms
from django.forms.widgets import SelectDateWidget


class CreateProjectForm(forms.Form):
    name = forms.CharField(label="Project name", max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
class CreateTaskForm(forms.Form):
    name = forms.CharField(
        label="Task name",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "style": "width: 20em"})
    )
    end_date = forms.DateField(
        label="End date",
        required=True,
        widget=SelectDateWidget(
            attrs={"class": "form-control", "style": "width: 20em; display: flex; flex-wrap: wrap; justify-content: space-between;"}
        )
    )
    users = forms.ChoiceField(
        label="Assign to user",
        choices=None,
        widget=forms.Select(attrs={"class": "form-control form-control-lg", "style": "width: 20em"})
    )

    def __init__(self, users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["users"].choices = users


class InviteUserForm(forms.Form):
    name = forms.CharField(
        label="User name",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "style": "width: 20em"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)