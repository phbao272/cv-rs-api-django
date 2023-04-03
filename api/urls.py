from django.urls import path
from . import views
from .recommender import cbf

urlpatterns = [
    path('get-my-resume', views.get_my_resume),
    path('get-all-job', views.get_all_jobs),

    path('testFn', cbf.testFn)
]
