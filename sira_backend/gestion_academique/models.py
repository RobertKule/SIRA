from django.db import models
from authentification.models import Utilisateur

class Etudiant(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profil_etudiant'
    )
    matricule = models.CharField(max_length=20, unique=True)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    genre = models.CharField(max_length=1, choices=[('M', 'Masculin'), ('F', 'Féminin'), ('X', 'Autre')])

class Enseignant(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profil_enseignant'
    )
    specialite = models.CharField(max_length=100)
    bureau = models.CharField(max_length=50)
    est_responsable = models.BooleanField(default=False)
    
# Dans gestion_academique/models.py

class Faculte(models.Model):
    nom = models.CharField(max_length=100)
    sigle = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.nom} ({self.sigle})"

class Departement(models.Model):
    nom = models.CharField(max_length=100)
    faculte = models.ForeignKey(Faculte, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nom

class AnneeAcademique(models.Model):
    libelle = models.CharField(max_length=20)
    date_debut = models.DateField()
    date_fin = models.DateField()
    est_active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.libelle

class Promotion(models.Model):
    nom = models.CharField(max_length=100)
    niveau = models.IntegerField()
    departement = models.ForeignKey(Departement, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.nom} (Niveau {self.niveau})"

class PromotionAnnuelle(models.Model):
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)
    annee = models.ForeignKey(AnneeAcademique, on_delete=models.CASCADE)
    responsable = models.ForeignKey(
        'Enseignant', 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='promotions_responsables'
    )
    
    class Meta:
        unique_together = ('promotion', 'annee')
    
    def __str__(self):
        return f"{self.promotion.nom} - {self.annee.libelle}"

class Cours(models.Model):
    code = models.CharField(max_length=20, unique=True)
    intitule = models.CharField(max_length=100)
    credits = models.IntegerField()
    heures_CM = models.IntegerField()
    heures_TP = models.IntegerField()
    
    def __str__(self):
        return f"{self.code} - {self.intitule}"

class CoursAnnuel(models.Model):
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)
    annee = models.ForeignKey(AnneeAcademique, on_delete=models.CASCADE)
    enseignant = models.ForeignKey(
        'Enseignant',
        on_delete=models.SET_NULL,
        null=True,
        related_name='cours_enseignes'
    )
    semestre = models.IntegerField(choices=[(1, 'Semestre 1'), (2, 'Semestre 2')])
    
    class Meta:
        unique_together = ('cours', 'annee', 'semestre')
    
    def __str__(self):
        return f"{self.cours.code} ({self.annee.libelle}) - S{self.semestre}"

class Inscription(models.Model):
    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('DESINSCRIT', 'Désinscrit'),
        ('DIPLOME', 'Diplômé'),
    ]
    
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    promotion_annuelle = models.ForeignKey(PromotionAnnuelle, on_delete=models.CASCADE)
    date_inscription = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')
    
    class Meta:
        unique_together = ('etudiant', 'promotion_annuelle')
    
    def __str__(self):
        return f"{self.etudiant} - {self.promotion_annuelle}"

class Resultat(models.Model):
    SESSION_CHOICES = [
        ('NORMALE', 'Session normale'),
        ('RATTRAPAGE', 'Session de rattrapage'),
    ]
    
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    cours_annuel = models.ForeignKey(CoursAnnuel, on_delete=models.CASCADE)
    note_tp = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    note_interro = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    note_examen = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    moyenne = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    mention = models.CharField(max_length=10, blank=True)
    session = models.CharField(max_length=20, choices=SESSION_CHOICES)
    
    class Meta:
        unique_together = ('etudiant', 'cours_annuel', 'session')
    
    def save(self, *args, **kwargs):
        # Calcul automatique de la moyenne si nécessaire
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.etudiant} - {self.cours_annuel} : {self.moyenne}"
