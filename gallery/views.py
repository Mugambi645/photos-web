from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from.forms import ImageUploadForm
from.models import Image, Collection,Tag
from django.contrib.auth.models import User
import torch
import torchvision
from torchvision import transforms



# Load a pre-trained image classification model (e.g., MobileNetV2)
model = torchvision.models.mobilenet_v2(pretrained=True)


#@login_required
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save(commit=False)
            #image_instance.submitter = request.user
            image_instance.save()

            img_path = image_instance.image_file.path
            img = torchvision.load_image(img_path)
            img = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])(img)

            img = img.unsqueeze(0)  # add batch dimension

            # Move the model and image to the GPU if available
            device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
            model.to(device)
            img = img.to(device)

            # Get predictions
            outputs = model(img)
            _, predicted = torch.max(outputs, 1)

            # Get the top 5 predictions
            _, indices = torch.topk(outputs, 5)
            predictions = [torch.nn.functional.softmax(outputs[0][index]) for index in indices[0]]

            # Create tags for the top 5 predictions
            for prediction, index in zip(predictions, indices[0]):
                label = torchvision.datasets.ImageNet.classes[index]
                tag, created = Tag.objects.get_or_create(name=label)
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