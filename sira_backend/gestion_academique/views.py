from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import (
    Faculte, Departement, AnneeAcademique, Promotion,
    PromotionAnnuelle, Cours, CoursAnnuel, Inscription, 
    Resultat, Etudiant, Enseignant
)
from .serializers import (
    FaculteSerializer, DepartementSerializer, AnneeAcademiqueSerializer,
    PromotionSerializer, PromotionAnnuelleSerializer, CoursSerializer,
    CoursAnnuelSerializer, InscriptionSerializer, ResultatSerializer,
    EnseignantSerializer, EtudiantSerializer
)

class FaculteViewSet(viewsets.ModelViewSet):
    queryset = Faculte.objects.all().order_by('nom')
    serializer_class = FaculteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom', 'sigle']

    @action(detail=True, methods=['get'])
    def departements(self, request, pk=None):
        departements = self.get_object().departement_set.all()
        serializer = DepartementSerializer(departements, many=True)
        return Response(serializer.data)

class DepartementViewSet(viewsets.ModelViewSet):
    queryset = Departement.objects.all().order_by('nom')
    serializer_class = DepartementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['faculte']
    search_fields = ['nom']

    @action(detail=True, methods=['get'])
    def promotions(self, request, pk=None):
        promotions = self.get_object().promotion_set.all()
        serializer = PromotionSerializer(promotions, many=True)
        return Response(serializer.data)

class AnneeAcademiqueViewSet(viewsets.ModelViewSet):
    queryset = AnneeAcademique.objects.all().order_by('-date_debut')
    serializer_class = AnneeAcademiqueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['libelle']

    @action(detail=False, methods=['get'])
    def active(self, request):
        annee = self.queryset.filter(est_active=True).first()
        if not annee:
            return Response({'detail': 'Aucune année active'}, status=404)
        serializer = self.get_serializer(annee)
        return Response(serializer.data)

class PromotionViewSet(viewsets.ModelViewSet):
    queryset = Promotion.objects.all().order_by('niveau', 'nom')
    serializer_class = PromotionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['departement', 'niveau']
    search_fields = ['nom']

class PromotionAnnuelleViewSet(viewsets.ModelViewSet):
    queryset = PromotionAnnuelle.objects.select_related(
        'promotion', 'annee', 'responsable'
    ).order_by('-annee__date_debut', 'promotion__niveau')
    serializer_class = PromotionAnnuelleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['promotion', 'annee', 'responsable']

    @action(detail=True, methods=['get'])
    def inscriptions(self, request, pk=None):
        inscriptions = self.get_object().inscription_set.filter(statut='ACTIF')
        serializer = InscriptionSerializer(inscriptions, many=True)
        return Response(serializer.data)

class CoursViewSet(viewsets.ModelViewSet):
    queryset = Cours.objects.all().order_by('code')
    serializer_class = CoursSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'intitule']

class CoursAnnuelViewSet(viewsets.ModelViewSet):
    queryset = CoursAnnuel.objects.select_related(
        'cours', 'annee', 'enseignant'
    ).order_by('-annee__date_debut', 'semestre', 'cours__code')
    serializer_class = CoursAnnuelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['cours', 'annee', 'enseignant', 'semestre']

    @action(detail=True, methods=['get'])
    def resultats(self, request, pk=None):
        resultats = self.get_object().resultat_set.all()
        serializer = ResultatSerializer(resultats, many=True)
        return Response(serializer.data)

class InscriptionViewSet(viewsets.ModelViewSet):
    queryset = Inscription.objects.select_related(
        'etudiant', 'promotion_annuelle'
    ).order_by('-date_inscription')
    serializer_class = InscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['etudiant', 'promotion_annuelle', 'statut']

    @action(detail=True, methods=['post'])
    def desinscrire(self, request, pk=None):
        inscription = self.get_object()
        inscription.statut = 'DESINSCRIT'
        inscription.save()
        return Response({'status': 'Désinscription effectuée'})

class ResultatViewSet(viewsets.ModelViewSet):
    queryset = Resultat.objects.select_related(
        'etudiant', 'cours_annuel'
    ).order_by('-cours_annuel__annee__date_debut', 'etudiant__utilisateur__last_name')
    serializer_class = ResultatSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['etudiant', 'cours_annuel', 'session']

    @action(detail=False, methods=['get'])
    def bulletin(self, request):
        etudiant_id = request.query_params.get('etudiant')
        annee_id = request.query_params.get('annee')
        
        if not all([etudiant_id, annee_id]):
            return Response(
                {'error': 'Paramètres etudiant et annee requis'},
                status=400
            )
            
        resultats = self.queryset.filter(
            etudiant_id=etudiant_id,
            cours_annuel__annee_id=annee_id
        )
        serializer = self.get_serializer(resultats, many=True)
        return Response(serializer.data)

class EnseignantViewSet(viewsets.ModelViewSet):
    queryset = Enseignant.objects.select_related('utilisateur').order_by('utilisateur__last_name')
    serializer_class = EnseignantSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        'utilisateur__first_name', 
        'utilisateur__last_name', 
        'specialite'
    ]
    filterset_fields = ['est_responsable']

    @action(detail=True, methods=['get'])
    def cours(self, request, pk=None):
        cours = self.get_object().cours_enseignes.all()
        serializer = CoursAnnuelSerializer(cours, many=True)
        return Response(serializer.data)

class EtudiantViewSet(viewsets.ModelViewSet):
    queryset = Etudiant.objects.select_related('utilisateur').order_by('utilisateur__last_name')
    serializer_class = EtudiantSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = [
        'matricule',
        'utilisateur__first_name',
        'utilisateur__last_name'
    ]
    filterset_fields = ['genre']