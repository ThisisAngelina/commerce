from django import forms
from .models import *

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['category', 'title', 'description', 'starting_bid', 'image_url']
                  