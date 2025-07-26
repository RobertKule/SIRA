from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='doc-index'),
    path('api/', views.api_routes, name='api-routes'),
    path('models/', views.models_doc, name='models-doc'),
    path('frontend/', views.frontend_guidelines, name='frontend-guidelines'),
]