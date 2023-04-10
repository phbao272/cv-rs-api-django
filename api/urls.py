from django.urls import path

from .analysis import resume, job
from . import views
from .recommender import cbf, cf, recommender

urlpatterns = [
    path('get-my-resume', views.get_my_resume),
    path('get-all-job', views.get_all_jobs),

    path('get-all-resume', resume.getAllResume),
    path('get-all-company', job.getAllCompany),

    path('get-by-cbf', cbf.getByCBF),
    path('get-by-cf', cf.getByCF),
    path('get-user-similarity', cf.getUserSimilarityById),

    path('get-recommend', recommender.getRecommend),

    path('similarity-matrix', cf.createDataSimilarity),




    # Chart
    path('get-resume-chart', resume.getResumeChart),
    path('get-company-chart', job.getCompanyChart),
    path('get-resume-pie-chart', resume.getResumePieChart),
]
