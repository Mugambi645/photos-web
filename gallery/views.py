from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from.forms import ImageUploadForm
from.models import Image, Collection,Tag
from django.contrib.auth.models import User
import torch
import torchvision
from torchvision import transforms


from django.core.files.base import ContentFile
import cv2
import numpy as np
import base64


import json
import urllib.request

# Load pre-trained MobileNetV2 model
model = torchvision.models.mobilenet_v2(pretrained=True)
model.eval()

# Load ImageNet class labels from GitHub
imagenet_url = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
with urllib.request.urlopen(imagenet_url) as f:
    imagenet_labels = [line.strip().decode("utf-8") for line in f.readlines()]

# Apply OpenCV filters
def apply_filter(img_path, filter_type):
    img = cv2.imread(img_path)

    if filter_type == 'grayscale':
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif filter_type == 'blur':
        img = cv2.GaussianBlur(img, (11, 11), 0)
    elif filter_type == 'edges':
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.Canny(gray, 100, 200)
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    cv2.imwrite(img_path, img)

# Upload view
# @login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)

            # Handle webcam base64 image (optional)
            webcam_data = request.POST.get('webcam_image')
            if webcam_data and not request.FILES.get('image_file'):
                format, imgstr = webcam_data.split(';base64,')
                ext = format.split('/')[-1]
                image_instance.image_file.save(
                    f'webcam_capture.{ext}',
                    ContentFile(base64.b64decode(imgstr)),
                    save=False
                )

            # Save instance only if image exists
            if image_instance.image_file:
                image_instance.save()
                form.save_m2m()
            else:
                form.add_error('image_file', "No image provided. Upload or capture a photo.")

            # Apply optional OpenCV filter
            selected_filter = form.cleaned_data.get('filter')
            if selected_filter and selected_filter != 'none':
                apply_filter(image_instance.image_file.path, selected_filter)

            # Load and transform image for classification
            img = torchvision.io.read_image(image_instance.image_file.path)
            img = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ConvertImageDtype(torch.float32),
                transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
            ])(img).unsqueeze(0)

            # Move to GPU if available
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model.to(device)
            img = img.to(device)

            with torch.no_grad():
                outputs = model(img)
                _, indices = torch.topk(outputs, 5)

                for idx in indices[0]:
                    label = imagenet_labels[idx] if idx < len(imagenet_labels) else f"Class-{idx.item()}"
                    tag, _ = Tag.objects.get_or_create(name=label)
                    image_instance.tags.add(tag)

            return redirect('core:index')
            
    else:
        form = ImageUploadForm()

    return render(request, 'gallery/upload.html', {'form': form})

"""
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

"""
def image_list(request):
    images = Image.objects.all().order_by('-upload_date')
    return render(request, 'gallery/_image_list.html', {'images': images})



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