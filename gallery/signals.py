from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Image
from .tasks import process_image_tags

@receiver(post_save, sender=Image)
def trigger_image_tagging(sender, instance, created, **kwargs):
    if created:
        process_image_tags.delay(instance.id)
