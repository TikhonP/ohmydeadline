from django.urls import path
from api import views


urlpatterns = [
    path('tips/', views.TipApiView.as_view()),
    path('deadlines/', views.DeadlineApiView.as_view()),
    path('profiles/', views.ProfileApiView.as_view()),
]
