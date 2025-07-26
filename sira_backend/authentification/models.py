from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'email est obligatoire')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hash automatique du mot de passe
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Utilisateur(AbstractUser):
    # Désactiver username (remplacé par email)
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Champs communs
    telephone = models.CharField(max_length=20, blank=True)
    date_inscription = models.DateField(auto_now_add=True)
    est_actif = models.BooleanField(default=True)
    
    # Champs Django requis
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UtilisateurManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Role(models.Model):
    nom = models.CharField(max_length=50, unique=True, choices=[
        ('ETUDIANT', 'Étudiant'),
        ('ENSEIGNANT', 'Enseignant'),
        ('ADMIN', 'Administrateur'),
    ])
    
    def __str__(self):
        return self.get_nom_display()

class UtilisateurRole(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('utilisateur', 'role')
    def __str__(self):
        return f"{self.utilisateur.email} - {self.role.nom}"