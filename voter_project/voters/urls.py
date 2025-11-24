from django.urls import path
from .views import *

urlpatterns = [
    path("create/", VoterCreateAPI.as_view()),
    path("approve/<int:pk>/", ApproveVoterAPI.as_view()),
    path("get/<int:pk>/", VoterGetAPI.as_view()),
    path("update/<int:pk>/", VoterUpdateAPI.as_view()),
    path("delete/<int:pk>/", VoterDeleteAPI.as_view()),
    path("search/", VoterSearchAPI.as_view()),
    path("download/<int:pk>/", VoterDownloadAPI.as_view()),

    #path('', views.VoterListCreate.as_view(), name='voter_list_create'), 
    #path('<int:pk>/', views.VoterRetrieveUpdateDelete.as_view(), name='voter_detail'),
    #path('generate_pdf/<int:pk>/', views.generate_voter_pdf, name='voter_pdf'),
    ]