from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Utilisateur
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    AdminEtudiantCreateSerializer,
    AdminEnseignantCreateSerializer
)

class LoginView(TokenObtainPairView):
    """
    Endpoint de connexion JWT personnalisé
    Renvoie les tokens d'accès/rafraîchissement + infos utilisateur
    """
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Gestion complète du profil utilisateur :
    - GET : Récupère toutes les informations du profil
    - PATCH : Met à jour partiellement les champs autorisés
    """
    queryset = Utilisateur.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch']  # Seules ces méthodes sont autorisées

    def get_serializer_class(self):
        """
        Choisit dynamiquement le serializer selon la méthode :
        - UserProfileSerializer pour la lecture (GET)
        - UserUpdateSerializer pour la mise à jour (PATCH)
        """
        if self.request.method == 'GET':
            return UserProfileSerializer
        return UserUpdateSerializer

    def get_object(self):
        """Renvoie toujours l'utilisateur actuellement connecté"""
        return self.request.user

    def patch(self, request, *args, **kwargs):
        """
        Gestion personnalisée des mises à jour partielles
        avec validation des données
        """
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Renvoie les données complètes après mise à jour
        return Response(
            UserProfileSerializer(instance).data,
            status=status.HTTP_200_OK
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    Endpoint dédié au changement de mot de passe
    Requiert :
    - old_password : mot de passe actuel
    - new_password : nouveau mot de passe (validé selon les règles Django)
    """
    serializer = ChangePasswordSerializer(
        data=request.data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        # Met à jour le mot de passe
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        
        # Envoyer un email de notification ici si nécessaire
        # send_password_change_email(request.user)
        
        return Response(
            {"status": "Mot de passe mis à jour avec succès"},
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminEtudiantCreateView(generics.CreateAPIView):
    """
    Endpoint ADMIN pour créer un nouveau compte étudiant
    Crée simultanément :
    - Le compte utilisateur de base
    - Le profil étudiant
    - Le rôle ETUDIANT
    """
    serializer_class = AdminEtudiantCreateSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminEnseignantCreateView(generics.CreateAPIView):
    """
    Endpoint ADMIN pour créer un nouveau compte enseignant
    Crée simultanément :
    - Le compte utilisateur de base
    - Le profil enseignant
    - Le rôle ENSEIGNANT
    """
    serializer_class = AdminEnseignantCreateSerializer
    permission_classes = [permissions.IsAdminUser]

# Fonction utilitaire optionnelle pour envoi d'email
# def send_password_change_email(user):
#     from django.core.mail import send_mail
#     subject = 'Votre mot de passe a été modifié'
#     message = f'Bonjour {user.first_name},\n\nVotre mot de passe a bien été mis à jour.'
#     send_mail(
#         subject,
#         message,
#         'no-reply@votredomaine.com',
#         [user.email],
#         fail_silently=False,
#     )