from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from gallery.models import Image, Collection

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    uploaded_images = Image.objects.filter(submitter=user).order_by('-upload_date')
    collections = Collection.objects.filter(owner=user).order_by('-name')

    return render(request, 'accounts/user_profile.html', {
        'profile_user': user,
        'uploaded_images': uploaded_images,
        'collections': collections,
    })
