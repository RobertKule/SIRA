from rest_framework import serializers
from .models import (
    Etudiant, Enseignant, Faculte, Departement, AnneeAcademique,
    Promotion, PromotionAnnuelle, Cours, CoursAnnuel, Inscription, Resultat
)
from authentification.models import Utilisateur

class FaculteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculte
        fields = '__all__'

class DepartementSerializer(serializers.ModelSerializer):
    faculte = FaculteSerializer(read_only=True)
    faculte_id = serializers.PrimaryKeyRelatedField(
        queryset=Faculte.objects.all(),
        source='faculte',
        write_only=True
    )
    
    class Meta:
        model = Departement
        fields = '__all__'

class AnneeAcademiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnneeAcademique
        fields = '__all__'
        extra_kwargs = {
            'date_debut': {'required': True},
            'date_fin': {'required': True}
        }

    def validate(self, data):
        if data['date_debut'] > data['date_fin']:
            raise serializers.ValidationError("La date de fin doit être postérieure à la date de début")
        return data
class EnseignantSerializer(serializers.ModelSerializer):
    # Champs utilisateur intégrés directement
    email = serializers.EmailField(source='utilisateur.email', required=True)
    password = serializers.CharField(source='utilisateur.password', write_only=True, required=False)
    nom = serializers.CharField(source='utilisateur.last_name', required=True)
    prenom = serializers.CharField(source='utilisateur.first_name', required=True)
    telephone = serializers.CharField(source='utilisateur.telephone', required=False)

    class Meta:
        model = Enseignant
        fields = [
            'utilisateur_id',  # Utilisez le nom du champ PK
            'email', 
            'password', 
            'nom', 
            'prenom', 
            'telephone',
            'specialite', 
            'bureau', 
            'est_responsable'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'utilisateur_id': {'read_only': True}  # Auto-généré
        }

    def create(self, validated_data):
        user_data = validated_data.pop('utilisateur')
        
        user = Utilisateur.objects.create_user(
            email=user_data['email'],
            password=user_data.get('password', 'defaultpassword'),
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            telephone=user_data.get('telephone', '')
        )
        
        enseignant = Enseignant.objects.create(
            utilisateur=user,
            **validated_data
        )
        return enseignant
    
class EtudiantSerializer(serializers.ModelSerializer):
    # Champs utilisateur intégrés
    email = serializers.EmailField(source='utilisateur.email', required=True)
    password = serializers.CharField(source='utilisateur.password', write_only=True, required=False)
    nom = serializers.CharField(source='utilisateur.last_name', required=True)
    prenom = serializers.CharField(source='utilisateur.first_name', required=True)
    telephone = serializers.CharField(source='utilisateur.telephone', required=False)

    class Meta:
        model = Etudiant
        fields = [
            'utilisateur_id',  # Nom correct du champ PK
            'email', 
            'password', 
            'nom', 
            'prenom', 
            'telephone',
            'matricule', 
            'date_naissance', 
            'lieu_naissance', 
            'genre'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'utilisateur_id': {'read_only': True}
        }

    def create(self, validated_data):
        user_data = validated_data.pop('utilisateur')
        
        user = Utilisateur.objects.create_user(
            email=user_data['email'],
            password=user_data.get('password', 'defaultpassword'),
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            telephone=user_data.get('telephone', '')
        )
        
        etudiant = Etudiant.objects.create(
            utilisateur=user,
            **validated_data
        )
        return etudiant  
class PromotionSerializer(serializers.ModelSerializer):
    departement = DepartementSerializer(read_only=True)
    departement_id = serializers.PrimaryKeyRelatedField(
        queryset=Departement.objects.all(),
        source='departement',
        write_only=True
    )
    
    class Meta:
        model = Promotion
        fields = '__all__'

class PromotionAnnuelleSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(read_only=True)
    promotion_id = serializers.PrimaryKeyRelatedField(
        queryset=Promotion.objects.all(),
        source='promotion',
        write_only=True
    )
    annee = AnneeAcademiqueSerializer(read_only=True)
    annee_id = serializers.PrimaryKeyRelatedField(
        queryset=AnneeAcademique.objects.all(),
        source='annee',
        write_only=True
    )
    responsable = EnseignantSerializer(read_only=True)
    responsable_id = serializers.PrimaryKeyRelatedField(
        queryset=Enseignant.objects.all(),
        source='responsable',
        write_only=True,
        allow_null=True
    )
    
    class Meta:
        model = PromotionAnnuelle
        fields = '__all__'

class CoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cours
        fields = '__all__'

class CoursAnnuelSerializer(serializers.ModelSerializer):
    cours = CoursSerializer(read_only=True)
    cours_id = serializers.PrimaryKeyRelatedField(
        queryset=Cours.objects.all(),
        source='cours',
        write_only=True
    )
    annee = AnneeAcademiqueSerializer(read_only=True)
    annee_id = serializers.PrimaryKeyRelatedField(
        queryset=AnneeAcademique.objects.all(),
        source='annee',
        write_only=True
    )
    enseignant = EnseignantSerializer(read_only=True)
    enseignant_id = serializers.PrimaryKeyRelatedField(
        queryset=Enseignant.objects.all(),
        source='enseignant',
        write_only=True,
        allow_null=True
    )
    
    class Meta:
        model = CoursAnnuel
        fields = '__all__'

class InscriptionSerializer(serializers.ModelSerializer):
    etudiant = EtudiantSerializer(read_only=True)
    etudiant_id = serializers.PrimaryKeyRelatedField(
        queryset=Etudiant.objects.all(),
        source='etudiant',
        write_only=True
    )
    promotion_annuelle = PromotionAnnuelleSerializer(read_only=True)
    promotion_annuelle_id = serializers.PrimaryKeyRelatedField(
        queryset=PromotionAnnuelle.objects.all(),
        source='promotion_annuelle',
        write_only=True
    )
    
    class Meta:
        model = Inscription
        fields = '__all__'

class ResultatSerializer(serializers.ModelSerializer):
    etudiant = EtudiantSerializer(read_only=True)
    etudiant_id = serializers.PrimaryKeyRelatedField(
        queryset=Etudiant.objects.all(),
        source='etudiant',
        write_only=True
    )
    cours_annuel = CoursAnnuelSerializer(read_only=True)
    cours_annuel_id = serializers.PrimaryKeyRelatedField(
        queryset=CoursAnnuel.objects.all(),
        source='cours_annuel',
        write_only=True
    )
    
    class Meta:
        model = Resultat
        fields = '__all__'
        
    def validate(self, data):
        for field in ['note_tp', 'note_interro', 'note_examen']:
            if field in data and data[field] is not None:
                if not (0 <= float(data[field]) <= 20):
                    raise serializers.ValidationError(
                        {field: "La note doit être comprise entre 0 et 20"}
                    )
        return data
        
    def calculate_moyenne(self, validated_data):
        notes = []
        weights = {'note_tp': 0.3, 'note_interro': 0.2, 'note_examen': 0.5}
        
        for field, weight in weights.items():
            if validated_data.get(field):
                notes.append(float(validated_data[field]) * weight)
                
        return sum(notes) if notes else None

    def create(self, validated_data):
        validated_data['moyenne'] = self.calculate_moyenne(validated_data)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data['moyenne'] = self.calculate_moyenne(validated_data)
        return super().update(instance, validated_data)