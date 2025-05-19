from django.urls import path
from . import views
app_name = "accounts"

urlpatterns = [
    path('user/<str:username>/', views.user_profile, name='user_profile'),
]