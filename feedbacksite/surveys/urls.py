from django.urls import path

from . import views

app_name = 'surveys'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/detail/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/',
         views.FeedbackCreate.as_view(success_url="submitted"),
         name='fill'),
    path('<int:survey_id>/submit/', views.submit, name='submit'),
    path('<int:pk>/submitted/', views.SubmittedView.as_view(), name='submitted'),
]
