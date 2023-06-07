from django import forms
from .models import *


class CartoonForm(forms.ModelForm):

    class Meta:
        model = Cartoon
        fields = ['name', 'cartoon_image']
