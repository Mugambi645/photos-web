
from celery import shared_task
from torchvision import models, transforms
import torch
from PIL import Image as PILImage
import os

from .models import Image, Tag

# Load model once (MobileNetV2)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.mobilenet_v2(pretrained=True)
model.eval().to(device)

# ImageNet class labels
from torchvision.models.mobilenetv2 import MobileNet_V2_Weights
weights = MobileNet_V2_Weights.DEFAULT
preprocess = weights.transforms()
class_labels = weights.meta['categories']

@shared_task
def process_image_tags(image_id):
    try:
        image_instance = Image.objects.get(id=image_id)

        if not image_instance.image_file:
            return "No image file associated"

        image_path = image_instance.image_file.path

        img = PILImage.open(image_path).convert('RGB')
        input_tensor = preprocess(img).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)

        # Get top 5 predictions
        top5 = torch.topk(probabilities, 5)
        labels = [class_labels[idx] for idx in top5.indices]

        for label in labels:
            tag, _ = Tag.objects.get_or_create(name=label)
            image_instance.tags.add(tag)

        image_instance.save()
        return f"Tags added: {', '.join(labels)}"

    except Image.DoesNotExist:
        return "Image not found"
