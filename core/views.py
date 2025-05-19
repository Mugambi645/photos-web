from django.shortcuts import render
from gallery.models import Image
import os
# Create your views here.

def index(request):
    images = Image.objects.all().order_by('-upload_date')

    # Filter out images that have no file or the file is missing
    images = [img for img in images if img.image_file and os.path.exists(img.image_file.path)]

    return render(request, 'core/index.html', {'images': images})