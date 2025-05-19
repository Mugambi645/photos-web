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


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404


from django.http import FileResponse, Http404
from django.conf import settings
import os


from sklearn.metrics.pairwise import cosine_similarity
from torchvision import models
from PIL import Image as PILImage



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
#@login_required
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

    # Filter out images that have no file or the file is missing
    images = [img for img in images if img.image_file and os.path.exists(img.image_file.path)]

    return render(request, 'gallery/_image_list.html', {'images': images})




@require_POST
@login_required
def toggle_like(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    liked = False

    if request.user in image.likes.all():
        image.likes.remove(request.user)
    else:
        image.likes.add(request.user)
        liked = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'likes_count': image.total_likes()
        })

    return redirect(request.META.get('HTTP_REFERER', 'core:index'))


def image_detail(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    return render(request, 'gallery/image_detail.html', {'image': image})



def download_image(request, image_id):
    from .models import Image
    image = get_object_or_404(Image, id=image_id)

    image.download_count += 1
    image.save()

    file_path = image.image_file.path
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    else:
        raise Http404("Image not found.")


#similar images


# Load pre-trained model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.mobilenet_v2(pretrained=True)
model.classifier = torch.nn.Identity()  # Remove classification layer
model.eval().to(device)

# Image transformation
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def get_image_embedding(img_path):
    img = PILImage.open(img_path).convert('RGB')
    img_tensor = transform(img).unsqueeze(0).to(device)  # Add batch dimension
    with torch.no_grad():
        features = model(img_tensor)
    features = features.cpu().numpy().flatten()
    normalized = features / np.linalg.norm(features)
    return normalized

def find_similar_images(request, image_id):
    query_image = get_object_or_404(Image, id=image_id)

    # Skip if query image has no file
    if not query_image.image_file or not query_image.image_file.path:
        return render(request, 'gallery/similar_images.html', {
            'query_image': query_image,
            'similar_images': [],
            'error': 'This image has no associated file.'
        })

    query_embedding = get_image_embedding(query_image.image_file.path)

    all_images = Image.objects.exclude(id=image_id)
    similarities = []

    for img in all_images:
        try:
            if not img.image_file or not img.image_file.path:
                continue
            embedding = get_image_embedding(img.image_file.path)
            similarity = cosine_similarity(
                query_embedding.reshape(1, -1),
                embedding.reshape(1, -1)
            )[0][0]
            similarities.append((img, similarity))
        except Exception as e:
            print(f"Skipping image {img.id}: {e}")
            continue

    similar_images = sorted(similarities, key=lambda x: x[1], reverse=True)[:6]

    return render(request, 'gallery/similar_images.html', {
        'query_image': query_image,
        'similar_images': similar_images,
    })
