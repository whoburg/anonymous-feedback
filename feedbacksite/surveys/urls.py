from django.urls import path

from . import views

app_name = 'surveys'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.form_fill, name='form_fill'),
    path('<int:pk>/fill/',
         views.FeedbackCreate.as_view(success_url="submitted"),
         name='fill'),
    path('<int:pk>/submit/', views.submit_feedback, name='submit'),
    path('<int:pk>/submitted/', views.SubmittedView.as_view(), name='submitted'),
]
