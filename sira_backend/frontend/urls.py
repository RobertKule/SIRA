from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    
    path('ajouter-etudiant/', views.admin_create_etudiant, name='admin_create_etudiant'),
    path('ajouter-enseignant/', views.admin_create_enseignant, name='admin_create_enseignant'),

]