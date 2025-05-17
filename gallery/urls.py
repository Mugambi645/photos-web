from . import views
from django.urls import path

app_name = "gallery"
urlpatterns = [
    path("upload/", views.upload_image, name="upload_image"),
]