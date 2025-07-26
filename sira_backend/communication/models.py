# Dans un nouveau fichier communication/models.py

from django.db import models

class Notification(models.Model):
    TYPE_CHOICES = [
        ('NOTE', 'Note'),
        ('ABSENCE', 'Absence'),
        ('PAIEMENT', 'Paiement'),
        ('AUTRE', 'Autre'),
    ]
    
    utilisateur = models.ForeignKey(
        'authentification.Utilisateur',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    contenu = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    date_creation = models.DateTimeField(auto_now_add=True)
    est_lue = models.BooleanField(default=False)
    lien = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.type} pour {self.utilisateur}"

class Message(models.Model):
    expediteur = models.ForeignKey(
        'authentification.Utilisateur',
        on_delete=models.CASCADE,
        related_name='messages_envoyes'
    )
    destinataire = models.ForeignKey(
        'authentification.Utilisateur',
        on_delete=models.CASCADE,
        related_name='messages_recus'
    )
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    est_archive = models.BooleanField(default=False)
    
    def __str__(self):
        return f"De {self.expediteur} à {self.destinataire}"

class GroupeMessage(models.Model):
    nom = models.CharField(max_length=100)
    date_creation = models.DateField(auto_now_add=True)
    membres = models.ManyToManyField(
        'authentification.Utilisateur',
        through='MembreGroupe',
        related_name='groupes'
    )
    
    def __str__(self):
        return self.nom

class MembreGroupe(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('MEMBRE', 'Membre'),
    ]
    
    groupe = models.ForeignKey(GroupeMessage, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey('authentification.Utilisateur', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBRE')
    
    class Meta:
        unique_together = ('groupe', 'utilisateur')
    
    def __str__(self):
        return f"{self.utilisateur} dans {self.groupe} ({self.role})"