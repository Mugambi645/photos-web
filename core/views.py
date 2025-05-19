from django.shortcuts import render
from gallery.models import Image
import os
# Create your views here.
import requests
from django.conf import settings
from django.db.models import Q
from django.shortcuts import render
from gallery.models import Image

def index(request):
    images = Image.objects.all().order_by('-upload_date')

    # Filter out images that have no file or the file is missing
    images = [img for img in images if img.image_file and os.path.exists(img.image_file.path)]

    return render(request, 'core/index.html', {'images': images})

#search functionality with unsplash API
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY')  

def search_images(request):
    query = request.GET.get('q')
    local_results = []
    unsplash_results = []

    if query:
        # Local database search
        local_results = Image.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).order_by('-upload_date')

        # Unsplash API search
        response = requests.get(
            'https://api.unsplash.com/search/photos',
            params={
                'query': query,
                'per_page': 9
            },
            headers={
                'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'
            }
        )

        if response.status_code == 200:
            data = response.json()
            unsplash_results = data.get('results', [])

    return render(request, 'core/search_results.html', {
        'query': query,
        'local_results': local_results,
        'unsplash_results': unsplash_results
    })
