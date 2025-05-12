from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from.forms import ImageUploadForm

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