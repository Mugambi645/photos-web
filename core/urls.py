from . import views
from django.urls import path


app_name = "core"

urlpatterns = [
    path("", views.index, name="index"),
    path('search/', views.search_images, name='search_images'),
]