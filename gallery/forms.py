

from django import forms
from .models import Image

FILTER_CHOICES = [
    ('none', 'No Filter'),
    ('grayscale', 'Grayscale'),
    ('blur', 'Blur'),
    ('edges', 'Edge Detection'),
]

class ImageUploadForm(forms.ModelForm):
    webcam_image = forms.CharField(widget=forms.HiddenInput(), required=False)
    filter = forms.ChoiceField(choices=FILTER_CHOICES, required=False)

    class Meta:
        model = Image
        fields = ('title', 'description', 'image_file')
