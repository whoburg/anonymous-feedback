from django.urls import path

from . import views

app_name = 'surveys'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.form_fill, name='form_fill'),
    path('<int:pk>/submitted/', views.SubmittedView.as_view(), name='submitted'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('signup/', views.signup, name='signup'),
]
