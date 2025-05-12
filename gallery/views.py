from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from.forms import ImageUploadForm
from.models import Image, Collection
from django.contrib.auth.models import User

#@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            #image_instance.submitter = request.user
            image_instance.save()
            return redirect('core:index') # Redirect to the home page or another success page
    else:
        form = ImageUploadForm()
    return render(request, 'gallery/upload.html', {'form': form})


def image_list(request):
    images = Image.objects.all().order_by('-upload_date')
    return render(request, 'gallery/image_list.html', {'images': images})



def search_images(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Image.objects.filter(
            Image.Q(title__icontains=query) | models.Q(description__icontains=query)
        ).order_by('-upload_date')
    return render(request, 'gallery/search_results.html', {'results': results, 'query': query})


def user_profile(request, username):
    user = User.objects.get(username=username)
    uploaded_images = Image.objects.filter(submitter=user).order_by('-upload_date')
    collections = Collection.objects.filter(owner=user).order_by('-name')
    return render(request, 'gallery/user_profile.html', {
        'profile_user': user,
        'uploaded_images': uploaded_images,
        'collections': collections,
    })