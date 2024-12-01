from django import forms


class CreateProjectForm(forms.Form):
    name = forms.CharField(label="Project name", max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update({"class": "form-control"})
