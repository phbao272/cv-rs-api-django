from django.urls import path
from . import views

urlpatterns = [
    path('get-my-resume', views.get_my_resume),
    path('get-all-job', views.get_all_jobs),
]
