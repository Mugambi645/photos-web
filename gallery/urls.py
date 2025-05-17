from . import views
from django.urls import path

app_name = "gallery"
urlpatterns = [
    path("upload/", views.upload_image, name="upload_image"),
    path('like/<int:image_id>/', views.toggle_like, name='toggle_like'),
    path('image/<int:image_id>/', views.image_detail, name='image_detail'),
]