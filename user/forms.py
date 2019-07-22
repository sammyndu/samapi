from django import forms
from .models import Person

class UserForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = {
            'firstname',
            'lastname',
            'gender',
            'date_of_birth',
        }

    def save(self, *args, **kwargs):
        lv = super().save(commit=False)
        lv.save()
        return lv