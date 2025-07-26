from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Faculte, Departement, AnneeAcademique, Promotion,
    PromotionAnnuelle, Cours, CoursAnnuel, Inscription, Resultat
)
from .serializers import (
    FaculteSerializer, DepartementSerializer, AnneeAcademiqueSerializer,
    PromotionSerializer, PromotionAnnuelleSerializer, CoursSerializer,
    CoursAnnuelSerializer, InscriptionSerializer, ResultatSerializer
)

# Faculté
class FaculteViewSet(viewsets.ModelViewSet):
    queryset = Faculte.objects.all().order_by('id')
    serializer_class = FaculteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom', 'sigle']

    @action(detail=True, methods=['get'])
    def departements(self, request, pk=None):
        faculte = self.get_object()
        departements = faculte.departement_set.all()
        serializer = DepartementSerializer(departements, many=True)
        return Response(serializer.data)


# Département
class DepartementViewSet(viewsets.ModelViewSet):
    queryset = Departement.objects.all().order_by('id')
    serializer_class = DepartementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['faculte']
    search_fields = ['nom']

    @action(detail=True, methods=['get'])
    def promotions(self, request, pk=None):
        departement = self.get_object()
        promotions = departement.promotion_set.all()
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)


# Année académique
class AnneeAcademiqueViewSet(viewsets.ModelViewSet):
    queryset = AnneeAcademique.objects.all().order_by('id').order_by('-date_debut')
    serializer_class = AnneeAcademiqueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['libelle']

    @action(detail=False, methods=['get'])
    def active(self, request):
        annee_active = AnneeAcademique.objects.filter(est_active=True).first()
        if not annee_active:
            return Response({'detail': 'Aucune année académique active'}, status=404)
        serializer = self.get_serializer(annee_active)
        return Response(serializer.data)


# Promotion
class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all().order_by('id')
    serializer_class = PromotionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['departement', 'niveau']
    search_fields = ['nom']


# Promotion Annuelle
class PromotionAnnuelleViewSet(viewsets.ModelViewSet):
    queryset = PromotionAnnuelle.objects.select_related('promotion', 'annee', 'responsable')
    serializer_class = PromotionAnnuelleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['promotion', 'annee', 'responsable']

    @action(detail=True, methods=['get'])
    def inscriptions(self, request, pk=None):
        promotion_annuelle = self.get_object()
        inscriptions = promotion_annuelle.inscription_set.filter(statut='ACTIF')
        serializer = InscriptionSerializer(inscriptions, many=True)
        return Response(serializer.data)


# Cours
class CoursViewSet(viewsets.ModelViewSet):
    queryset = Cours.objects.all().order_by('id')
    serializer_class = CoursSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'intitule']


# Cours Annuel
class CoursAnnuelViewSet(viewsets.ModelViewSet):
    queryset = CoursAnnuel.objects.select_related('cours', 'annee', 'enseignant')
    serializer_class = CoursAnnuelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cours', 'annee', 'enseignant', 'semestre']

    @action(detail=True, methods=['get'])
    def resultats(self, request, pk=None):
        cours_annuel = self.get_object()
        resultats = cours_annuel.resultat_set.all()
        serializer = ResultatSerializer(resultats, many=True)
        return Response(serializer.data)


# Inscription
class InscriptionViewSet(viewsets.ModelViewSet):
    queryset = Inscription.objects.select_related('etudiant', 'promotion_annuelle')
    serializer_class = InscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['etudiant', 'promotion_annuelle', 'statut']

    @action(detail=True, methods=['post'])
    def desinscrire(self, request, pk=None):
        inscription = self.get_object()
        inscription.statut = 'DESINSCRIT'
        inscription.save()
        serializer = self.get_serializer(inscription)
        return Response(serializer.data)


# Résultat
class ResultatViewSet(viewsets.ModelViewSet):
    queryset = Resultat.objects.select_related('etudiant', 'cours_annuel')
    serializer_class = ResultatSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['etudiant', 'cours_annuel', 'session']

    @action(detail=False, methods=['get'])
    def bulletin(self, request):
        etudiant_id = request.query_params.get('etudiant')
        annee_id = request.query_params.get('annee')

        if not etudiant_id or not annee_id:
            return Response(
                {'error': 'Les paramètres etudiant et annee sont requis'},
                status=400
            )

        resultats = Resultat.objects.filter(
            etudiant_id=etudiant_id,
            cours_annuel__annee_id=annee_id
        ).select_related('cours_annuel__cours')

        serializer = self.get_serializer(resultats, many=True)
        return Response(serializer.data)
