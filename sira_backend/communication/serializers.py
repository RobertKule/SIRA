from rest_framework import serializers
from .models import Notification, Message, GroupeMessage, MembreGroupe
from authentification.models import Utilisateur

class NotificationSerializer(serializers.ModelSerializer):
    utilisateur_id = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.all(),
        source='utilisateur',
        write_only=True
    )
    utilisateur_nom = serializers.CharField(
        source='utilisateur.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Notification
        fields = [
            'id', 'utilisateur_id', 'utilisateur_nom', 'contenu', 'type',
            'date_creation', 'est_lue', 'lien'
        ]
        read_only_fields = ['date_creation']
    
    def validate_type(self, value):
        if value not in dict(Notification.TYPE_CHOICES):
            raise serializers.ValidationError("Type de notification invalide")
        return value

class MessageSerializer(serializers.ModelSerializer):
    expediteur_id = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.all(),
        source='expediteur',
        write_only=True
    )
    expediteur_nom = serializers.CharField(
        source='expediteur.get_full_name',
        read_only=True
    )
    destinataire_id = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.all(),
        source='destinataire',
        write_only=True
    )
    destinataire_nom = serializers.CharField(
        source='destinataire.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Message
        fields = [
            'id', 'expediteur_id', 'expediteur_nom', 'destinataire_id',
            'destinataire_nom', 'contenu', 'date_envoi', 'est_archive'
        ]
        read_only_fields = ['date_envoi']

class MembreGroupeSerializer(serializers.ModelSerializer):
    utilisateur_id = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.all(),
        source='utilisateur',
        write_only=True
    )
    utilisateur_nom = serializers.CharField(
        source='utilisateur.get_full_name',
        read_only=True
    )
    groupe_nom = serializers.CharField(
        source='groupe.nom',
        read_only=True
    )
    
    class Meta:
        model = MembreGroupe
        fields = [
            'id', 'groupe', 'groupe_nom', 'utilisateur_id', 'utilisateur_nom',
            'role'
        ]
    
    def validate_role(self, value):
        if value not in dict(MembreGroupe.ROLE_CHOICES):
            raise serializers.ValidationError("Rôle invalide")
        return value

class GroupeMessageSerializer(serializers.ModelSerializer):
    membres = MembreGroupeSerializer(
        source='membregroupe_set',
        many=True,
        read_only=True
    )
    createur_id = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.all(),
        source='createur',
        write_only=True,
        required=False
    )
    createur_nom = serializers.CharField(
        source='createur.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = GroupeMessage
        fields = [
            'id', 'nom', 'date_creation', 'createur_id', 'createur_nom',
            'membres'
        ]
        read_only_fields = ['date_creation']
    
    def create(self, validated_data):
        membres_data = validated_data.pop('membres', [])
        groupe = GroupeMessage.objects.create(**validated_data)
        
        # Ajout automatique du créateur comme admin
        if 'createur' in validated_data:
            MembreGroupe.objects.create(
                groupe=groupe,
                utilisateur=validated_data['createur'],
                role='ADMIN'
            )
        
        return groupe

class GroupeMessageDetailSerializer(GroupeMessageSerializer):
    messages = serializers.SerializerMethodField()
    
    class Meta(GroupeMessageSerializer.Meta):
        fields = GroupeMessageSerializer.Meta.fields + ['messages']
    
    def get_messages(self, obj):
        messages = obj.message_set.all().order_by('-date_envoi')[:50]
        return MessageSerializer(messages, many=True).data

class AjoutMembreSerializer(serializers.Serializer):
    utilisateur_id = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.all()
    )
    role = serializers.ChoiceField(choices=MembreGroupe.ROLE_CHOICES)
    
    def create(self, validated_data):
        groupe = self.context['groupe']
        utilisateur = validated_data['utilisateur_id']
        role = validated_data['role']
        
        membre, created = MembreGroupe.objects.get_or_create(
            groupe=groupe,
            utilisateur=utilisateur,
            defaults={'role': role}
        )
        
        if not created:
            membre.role = role
            membre.save()
        
        return membre