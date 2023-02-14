from django.urls import path
from . import views

urlpatterns = [
    path('calc-tfidf', views.calcTFIDF),
]
