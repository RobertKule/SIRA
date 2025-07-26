# communication/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'groupes', views.GroupeMessageViewSet, basename='groupe')
router.register(r'membres-groupes', views.MembreGroupeViewSet, basename='membre-groupe')

urlpatterns = [
    path('', include(router.urls)),
]