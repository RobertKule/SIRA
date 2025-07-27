from django.db import models
from django.db.models import Q
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters  # Ajoutez cette ligne
from .models import Notification, Message, GroupeMessage, MembreGroupe
from .serializers import (
    NotificationSerializer, 
    MessageSerializer,
    GroupeMessageSerializer, 
    GroupeMessageDetailSerializer,
    AjoutMembreSerializer,
    MembreGroupeSerializer
)

class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.none()  # Requête vide par défaut

    def get_queryset(self):
        """
        Retourne uniquement les notifications de l'utilisateur connecté
        """
        return Notification.objects.filter(
            utilisateur=self.request.user
        ).select_related('utilisateur').order_by('-date_creation')

    @action(detail=True, methods=['post'])
    def marquer_comme_lue(self, request, pk=None):
        """
        Marque une notification comme lue
        """
        notification = self.get_object()
        notification.est_lue = True
        notification.save()
        return Response(
            {'status': 'notification marquée comme lue'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def non_lues(self, request):
        """
        Liste toutes les notifications non lues
        """
        notifications = self.get_queryset().filter(est_lue=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la messagerie privée
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Message.objects.none()
    filter_backends = [filters.SearchFilter]
    search_fields = ['contenu']

    def get_queryset(self):
        """
        Retourne les messages envoyés ou reçus par l'utilisateur
        """
        user = self.request.user
        return Message.objects.filter(
            Q(expediteur=user) | Q(destinataire=user)
        ).select_related(
            'expediteur',
            'destinataire'
        ).order_by('-date_envoi')

    @action(detail=False, methods=['get'])
    def conversations(self, request):
        """
        Liste les conversations (dernier message avec chaque contact)
        """
        user = request.user
        # Sous-requête pour obtenir les derniers messages
        last_messages = Message.objects.filter(
            Q(expediteur=user) | Q(destinataire=user)
        ).values(
            'expediteur', 'destinataire'
        ).annotate(
            max_date=models.Max('date_envoi')
        )

        conversations = []
        for msg in last_messages:
            conversation = Message.objects.filter(
                Q(expediteur=msg['expediteur'], destinaire=msg['destinataire']) |
                Q(expediteur=msg['destinataire'], destinaire=msg['expediteur']),
                date_envoi=msg['max_date']
            ).first()
            if conversation:
                conversations.append(conversation)

        serializer = self.get_serializer(conversations, many=True)
        return Response(serializer.data)

class GroupeMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des groupes de discussion
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = GroupeMessage.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['nom']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GroupeMessageDetailSerializer
        return GroupeMessageSerializer

    def get_queryset(self):
        """
        Filtre les groupes où l'utilisateur est membre
        """
        user = self.request.user
        return GroupeMessage.objects.filter(
            membres__utilisateur=user
        ).prefetch_related(
            'membres',
            'membres__utilisateur'
        ).distinct()

    @action(detail=True, methods=['get'])
    def membres(self, request, pk=None):
        """
        Liste tous les membres d'un groupe
        """
        groupe = self.get_object()
        membres = groupe.membregroupe_set.all()
        serializer = MembreGroupeSerializer(membres, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def ajouter_membre(self, request, pk=None):
        """
        Ajoute un membre à un groupe
        """
        groupe = self.get_object()
        serializer = AjoutMembreSerializer(
            data=request.data,
            context={'groupe': groupe, 'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def quitter_groupe(self, request, pk=None):
        """
        Permet à un utilisateur de quitter un groupe
        """
        groupe = self.get_object()
        user = request.user
        
        try:
            membre = MembreGroupe.objects.get(
                groupe=groupe,
                utilisateur=user
            )
            membre.delete()
            return Response(
                {'status': 'Vous avez quitté le groupe'},
                status=status.HTTP_200_OK
            )
        except MembreGroupe.DoesNotExist:
            return Response(
                {'error': 'Vous n\'êtes pas membre de ce groupe'},
                status=status.HTTP_400_BAD_REQUEST
            )

class MembreGroupeViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des membres de groupe
    """
    serializer_class = MembreGroupeSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = MembreGroupe.objects.all()

    def get_queryset(self):
        """
        Filtre les appartenances de l'utilisateur
        """
        return MembreGroupe.objects.filter(
            utilisateur=self.request.user
        ).select_related('groupe', 'utilisateur')

    @action(detail=True, methods=['post'])
    def modifier_role(self, request, pk=None):
        """
        Change le rôle d'un membre (admin seulement)
        """
        membre = self.get_object()
        nouveau_role = request.data.get('role')
        
        if nouveau_role not in dict(MembreGroupe.ROLE_CHOICES):
            return Response(
                {'error': 'Rôle invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que le demandeur est admin du groupe
        if not MembreGroupe.objects.filter(
            groupe=membre.groupe,
            utilisateur=request.user,
            role='ADMIN'
        ).exists():
            return Response(
                {'error': 'Seuls les administrateurs peuvent modifier les rôles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        membre.role = nouveau_role
        membre.save()
        return Response(
            {'status': f'Rôle changé à {nouveau_role}'},
            status=status.HTTP_200_OK
        ) 