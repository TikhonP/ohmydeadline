from django.urls import path
from . import views


urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('login/', views.loginp, name='login'),
    path('register/', views.registerp, name='register'),
    path('logout/', views.logoutp, name='logout'),
    path('adddeadline/', views.adddeadline, name='adddeadline'),
    path('donedeadline/', views.done_task, name='donedeadline'),
]
