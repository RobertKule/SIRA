from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'facultes', views.FaculteViewSet)
router.register(r'departements', views.DepartementViewSet)
router.register(r'annees-academiques', views.AnneeAcademiqueViewSet)
router.register(r'promotions', views.PromotionViewSet)
router.register(r'promotions-annuelles', views.PromotionAnnuelleViewSet)
router.register(r'cours', views.CoursViewSet)
router.register(r'cours-annuels', views.CoursAnnuelViewSet)
router.register(r'inscriptions', views.InscriptionViewSet)
router.register(r'resultats', views.ResultatViewSet)
router.register(r'enseignants', views.EnseignantViewSet)
router.register(r'etudiants', views.EtudiantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]