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