from rest_framework import serializers
from .models import (
    Etudiant, Enseignant, Faculte, Departement, AnneeAcademique,
    Promotion, PromotionAnnuelle, Cours, CoursAnnuel, Inscription, Resultat
)
from authentification.models import Utilisateur

# ==== Sérialiseurs de base ====

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
        
    def validate(self, data):
        if data['date_debut'] > data['date_fin']:
            raise serializers.ValidationError("La date de fin doit être postérieure à la date de début")
        return data

# ==== Sérialiseurs pour les utilisateurs spécialisés ====

class EtudiantSerializer(serializers.ModelSerializer):
    utilisateur_id = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.all(),
        source='utilisateur',
        write_only=True
    )
    nom = serializers.CharField(source='utilisateur.last_name', read_only=True)
    prenom = serializers.CharField(source='utilisateur.first_name', read_only=True)
    email = serializers.EmailField(source='utilisateur.email', read_only=True)

    class Meta:
        model = Etudiant
        fields = '__all__'
        extra_fields = ['nom', 'prenom', 'email']

class EnseignantSerializer(serializers.ModelSerializer):
    utilisateur_id = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.all(),
        source='utilisateur',
        write_only=True
    )
    nom = serializers.CharField(source='utilisateur.last_name', read_only=True)
    prenom = serializers.CharField(source='utilisateur.first_name', read_only=True)
    email = serializers.EmailField(source='utilisateur.email', read_only=True)

    class Meta:
        model = Enseignant
        fields = '__all__'
        extra_fields = ['nom', 'prenom', 'email']

# ==== Sérialiseurs pour la structure académique ====

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

# ==== Sérialiseurs pour les cours ====

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

# ==== Sérialiseurs pour les inscriptions et résultats ====

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
        # Validation des notes entre 0 et 20
        for field in ['note_tp', 'note_interro', 'note_examen']:
            if field in data and data[field] is not None:
                if not (0 <= data[field] <= 20):
                    raise serializers.ValidationError(
                        {field: "La note doit être comprise entre 0 et 20"}
                    )
        return data
        
    def calculate_moyenne(self, validated_data):
        # Exemple de calcul de moyenne (à adapter selon votre logique métier)
        notes = []
        if validated_data.get('note_tp'):
            notes.append(validated_data['note_tp'] * 0.3)  # 30% du TP
        if validated_data.get('note_interro'):
            notes.append(validated_data['note_interro'] * 0.2)  # 20% de l'interro
        if validated_data.get('note_examen'):
            notes.append(validated_data['note_examen'] * 0.5)  # 50% de l'examen
            
        if notes:
            return sum(notes)
        return None

    def create(self, validated_data):
        validated_data['moyenne'] = self.calculate_moyenne(validated_data)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data['moyenne'] = self.calculate_moyenne(validated_data)
        return super().update(instance, validated_data)