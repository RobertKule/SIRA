from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authentification.urls')),
    path('gestion/', include('gestion_academique.urls')),
    path('communication/', include('communication.urls')),
    path('docs/', include('docs.urls')),
    path('', include('frontend.urls')),
]