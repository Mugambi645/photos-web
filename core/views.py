from django.shortcuts import render
from gallery.models import Image
# Create your views here.

def index(request):
    images = Image.objects.all().order_by('-upload_date')
    return render(request, 'core/index.html', {'images': images})
