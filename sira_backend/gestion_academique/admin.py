from django.contrib import admin
from .models import Etudiant, Enseignant

@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'utilisateur', 'genre')

@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ('specialite', 'utilisateur', 'est_responsable')