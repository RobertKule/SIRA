from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re
from .models import Utilisateur, Role, UtilisateurRole
from gestion_academique.models import Etudiant, Enseignant

def validate_phone_number(value):
    """
    Validation personnalisée pour les numéros de téléphone congolais
    Format: +243 suivi de 9 chiffres
    """
    if not re.match(r'^\+243[0-9]{9}$', value):
        raise ValidationError("Le numéro doit être au format congolais (+243XXXXXXXXX)")

class CustomTokenObtainPairSerializer(serializers.TokenObtainPairSerializer):
    """
    Serializer JWT personnalisé qui ajoute des informations utilisateur
    dans la réponse des tokens
    """
    def validate(self, attrs):
        # Validation standard du token
        data = super().validate(attrs)
        user = self.user
        
        # Ajout des informations supplémentaires
        data.update({
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'roles': list(user.roles.values_list('role__nom', flat=True)),
            'profile_type': self.get_profile_type(user),
            'telephone': user.telephone
        })
        return data

    def get_profile_type(self, user):
        """Détermine le type de profil de l'utilisateur"""
        if hasattr(user, 'profil_etudiant'):
            return 'etudiant'
        elif hasattr(user, 'profil_enseignant'):
            return 'enseignant'
        return 'admin'

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer complet pour la lecture du profil utilisateur
    Inclut toutes les informations (lecture seule)
    """
    roles = serializers.SerializerMethodField()
    profile_type = serializers.SerializerMethodField()
    matricule = serializers.SerializerMethodField()
    specialite = serializers.SerializerMethodField()

    class Meta:
        model = Utilisateur
        fields = [
            'id', 'email', 'first_name', 'last_name', 'telephone',
            'date_inscription', 'roles', 'profile_type', 'matricule', 'specialite'
        ]
        read_only_fields = fields  # Tous les champs en lecture seule

    def get_roles(self, obj):
        """Récupère la liste des noms de rôles"""
        return list(obj.roles.values_list('role__nom', flat=True))

    def get_profile_type(self, obj):
        """Détermine le type de profil"""
        if hasattr(obj, 'profil_etudiant'):
            return 'etudiant'
        elif hasattr(obj, 'profil_enseignant'):
            return 'enseignant'
        return 'admin'

    def get_matricule(self, obj):
        """Récupère le matricule étudiant si existe"""
        return getattr(obj.profil_etudiant, 'matricule', None)

    def get_specialite(self, obj):
        """Récupère la spécialité enseignant si existe"""
        return getattr(obj.profil_enseignant, 'specialite', None)

class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour des informations utilisateur
    Champs modifiables uniquement
    """
    telephone = serializers.CharField(
        validators=[validate_phone_number],
        required=False
    )

    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'telephone']
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False}
        }

    def validate_telephone(self, value):
        """Validation supplémentaire du téléphone"""
        if len(value) != 13:
            raise serializers.ValidationError("Le numéro doit contenir 12 chiffres après le +243")
        return value

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer pour le changement de mot de passe
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        min_length=8
    )

    def validate_old_password(self, value):
        """Vérifie que l'ancien mot de passe est correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("L'ancien mot de passe est incorrect")
        return value

    def validate_new_password(self, value):
        """Valide le nouveau mot de passe selon les règles Django"""
        user = self.context['request'].user
        validate_password(value, user)
        
        # Empêche la réutilisation de l'ancien mot de passe
        if user.check_password(value):
            raise serializers.ValidationError("Le nouveau mot de passe doit être différent de l'ancien")
        
        return value

class AdminEtudiantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'étudiants par l'admin
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = Etudiant
        fields = [
            'email', 'password', 'first_name', 'last_name',
            'matricule', 'date_naissance', 'lieu_naissance', 'genre'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'matricule': {'required': True}
        }

    def create(self, validated_data):
        """Crée l'utilisateur et le profil étudiant"""
        user_data = {
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name')
        }
        
        user = Utilisateur.objects.create_user(**user_data)
        
        # Attribution du rôle étudiant
        role = Role.objects.get(nom='ETUDIANT')
        UtilisateurRole.objects.create(utilisateur=user, role=role)
        
        # Création du profil étudiant
        return Etudiant.objects.create(utilisateur=user, **validated_data)

class AdminEnseignantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'enseignants par l'admin
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = Enseignant
        fields = [
            'email', 'password', 'first_name', 'last_name',
            'specialite', 'bureau', 'est_responsable'
        ]

    def create(self, validated_data):
        """Crée l'utilisateur et le profil enseignant"""
        user_data = {
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name')
        }
        
        user = Utilisateur.objects.create_user(**user_data)
        
        # Attribution du rôle enseignant
        role = Role.objects.get(nom='ENSEIGNANT')
        UtilisateurRole.objects.create(utilisateur=user, role=role)
        
        # Création du profil enseignant
        return Enseignant.objects.create(utilisateur=user, **validated_data)