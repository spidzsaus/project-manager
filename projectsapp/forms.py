from django import forms
from django.forms.widgets import SelectDateWidget
from fastapi import dependencies


class CreateProjectForm(forms.Form):
    name = forms.CharField(label="Project name", max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})


class CreateTaskForm(forms.Form):
    name = forms.CharField(
        label="Task name",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control form-control-lg", "style": "width: 20em"}
        ),
    )

    description = forms.CharField(
        label="Task description",
        widget=forms.Textarea(
            attrs={"class": "form-control form-control-lg", "style": "width: 20em"}
        ),
    )

    end_date = forms.DateField(
        label="End date",
        required=True,
        widget=SelectDateWidget(
            attrs={
                "class": "form-control",
                "style": "width: 20em; display: flex; flex-wrap: wrap; justify-content: space-between;",
            }
        ),
    )
    users = forms.ChoiceField(
        label="Assign to user",
        choices=[],
        widget=forms.Select(
            attrs={"class": "form-control form-control-lg", "style": "width: 20em"}
        ),
    )

    depends_on = forms.MultipleChoiceField(
        label="Depends on",
        choices=[],
        required=False,
        widget=forms.SelectMultiple(
            attrs={"class": "form-control form-control-lg", "style": "width: 20em"}
        ),
    )

    def __init__(self, users, tasks, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["users"].choices = users
        self.fields["depends_on"].choices = tasks


class InviteUserForm(forms.Form):
    name = forms.CharField(
        label="User name",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control form-control-lg", "style": "width: 20em"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AssignUserForm(forms.Form):
    user = forms.ChoiceField(
        label="Team Member",
        choices=[],
        widget=forms.Select(
            attrs={"class": "form-control form-control-lg", "style": "width: 20em"}
        ),
    )

    def __init__(self, users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].choices = users


class AssignDependencyForm(forms.Form):
    dependency_task = forms.ChoiceField(
        label="Add dependencies",
        choices=[],
        required=False,
        widget=forms.Select(
            attrs={"class": "form-control form-control-lg", "style": "width: 20em"}
        ),
    )

    def __init__(self, tasks, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dependency_task"].choices = tasks
