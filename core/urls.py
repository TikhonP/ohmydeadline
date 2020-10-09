from django.urls import path
from . import views


urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('login/', views.loginp, name='login'),
    path('register/', views.registerp, name='register'),
    path('logout/', views.logoutp, name='logout'),
    path('adddeadline/', views.adddeadline, name='adddeadline'),
    path('donedeadline/', views.done_task, name='donedeadline'),
    path('all_tasks/', views.all_tasks, name='all_tasks'),
    path('unpin/', views.unpin_tip, name='unpin'),
    path('addtip/', views.add_tip, name='add_tip'),
    path('profile/', views.profilep, name='profile'),
    path('profile/delete_telegram/', views.unpin_telegram, name='delete_telegram'),
]
