from django.urls import path
from .views import (
    AdminEtudiantCreateView, 
    AdminEnseignantCreateView,
    LoginView,
    UserProfileView,
    change_password
)

urlpatterns = [
    path('admin/create-etudiant/', AdminEtudiantCreateView.as_view(), name='admin-create-etudiant'),
    path('admin/create-enseignant/', AdminEnseignantCreateView.as_view(), name='admin-create-enseignant'),
    path('login/', LoginView.as_view(), name='login'),
    path('me/', UserProfileView.as_view(), name='current-user'),
    path('me/password/', change_password, name='change-password'),
]
