# Sauvegardez ce code dans un fichier init_sira.py puis exécutez :
# python manage.py shell < init_sira.py

from django.contrib.auth import get_user_model
from authentification.models import Role, UtilisateurRole
from gestion_academique.models import (
    Faculte, Departement, AnneeAcademique, Promotion,
    PromotionAnnuelle, Cours, CoursAnnuel, Etudiant, Enseignant,
    Inscription, Resultat
)
from communication.models import (
    Notification, Message, GroupeMessage, MembreGroupe
)
from django.utils import timezone
import random

User = get_user_model()

def init_system():
    print("Initialisation du système SIRA...")
    
    # 1. Création des rôles
    print("Création des rôles...")
    roles = ['ETUDIANT', 'ENSEIGNANT', 'ADMIN']
    for role in roles:
        Role.objects.get_or_create(nom=role)
    
    # 2. Création des utilisateurs de test
    print("Création des utilisateurs...")
    admin = User.objects.create_superuser(
        email='admin@sira.com',
        password='admin123',
        first_name='Admin',
        last_name='SIRA'
    )
    UtilisateurRole.objects.create(utilisateur=admin, role=Role.objects.get(nom='ADMIN'))
    
    enseignants = []
    for i in range(1, 4):
        enseignant = User.objects.create_user(
            email=f'enseignant{i}@sira.com',
            password=f'enseignant{i}',
            first_name=f'Enseignant{i}',
            last_name='Professeur'
        )
        UtilisateurRole.objects.create(utilisateur=enseignant, role=Role.objects.get(nom='ENSEIGNANT'))
        enseignants.append(enseignant)
    
    etudiants = []
    for i in range(1, 11):
        etudiant = User.objects.create_user(
            email=f'etudiant{i}@sira.com',
            password=f'etudiant{i}',
            first_name=f'Étudiant{i}',
            last_name='Test'
        )
        UtilisateurRole.objects.create(utilisateur=etudiant, role=Role.objects.get(nom='ETUDIANT'))
        etudiants.append(etudiant)
    
    # 3. Initialisation gestion académique
    print("Initialisation de la gestion académique...")
    
    # Facultés et départements
    faculte_sciences = Faculte.objects.create(nom='Faculté des Sciences', sigle='FS')
    departement_info = Departement.objects.create(nom='Informatique', faculte=faculte_sciences)
    departement_math = Departement.objects.create(nom='Mathématiques', faculte=faculte_sciences)
    
    # Années académiques
    annee_en_cours = AnneeAcademique.objects.create(
        libelle='2023-2024',
        date_debut=timezone.datetime(2023, 9, 1).date(),
        date_fin=timezone.datetime(2024, 8, 31).date(),
        est_active=True
    )
    
    # Promotions
    promo_info_l1 = Promotion.objects.create(
        nom='Licence 1 Informatique',
        niveau=1,
        departement=departement_info
    )
    
    # Promotions annuelles
    promo_annuelle = PromotionAnnuelle.objects.create(
        promotion=promo_info_l1,
        annee=annee_en_cours,
        responsable=Enseignant.objects.create(
            utilisateur=enseignants[0],
            specialite='Informatique Fondamentale',
            bureau='Bâtiment A, Bureau 101'
        )
    )
    
    # Cours
    cours_algo = Cours.objects.create(
        code='INF101',
        intitule='Algorithmique',
        credits=5,
        heures_CM=30,
        heures_TP=20
    )
    
    # Cours annuels
    cours_annuel_algo = CoursAnnuel.objects.create(
        cours=cours_algo,
        annee=annee_en_cours,
        enseignant=Enseignant.objects.get(utilisateur=enseignants[0]),
        semestre=1
    )
    
    # Étudiants et inscriptions
    for i, etudiant_user in enumerate(etudiants[:5]):
        etudiant = Etudiant.objects.create(
            utilisateur=etudiant_user,
            matricule=f'MAT2023{i:03d}',
            date_naissance=timezone.datetime(2000, 1, 1).date(),
            lieu_naissance='Ville Test',
            genre='M'
        )
        Inscription.objects.create(
            etudiant=etudiant,
            promotion_annuelle=promo_annuelle,
            statut='ACTIF'
        )
    
    # Résultats
    for etudiant in Etudiant.objects.all():
        Resultat.objects.create(
            etudiant=etudiant,
            cours_annuel=cours_annuel_algo,
            note_tp=random.uniform(10, 20),
            note_interro=random.uniform(10, 20),
            note_examen=random.uniform(10, 20),
            session='NORMALE'
        )
    
    # 4. Initialisation communication
    print("Initialisation du module de communication...")
    
    # Notifications
    for etudiant_user in etudiants[:3]:
        Notification.objects.create(
            utilisateur=etudiant_user,
            contenu='Votre note d\'algorithmique a été publiée',
            type='NOTE',
            lien='/resultats/'
        )
    
    # Messages
    Message.objects.create(
        expediteur=enseignants[0],
        destinataire=etudiants[0],
        contenu='Bonjour, pensez à rendre votre TP avant vendredi.'
    )
    
    # Groupes de discussion
    groupe_tp = GroupeMessage.objects.create(nom='Groupe TP Algorithmique')
    for etudiant in etudiants[:5]:
        MembreGroupe.objects.create(
            groupe=groupe_tp,
            utilisateur=etudiant,
            role='MEMBRE'
        )
    MembreGroupe.objects.create(
        groupe=groupe_tp,
        utilisateur=enseignants[0],
        role='ADMIN'
    )
    
    print("Initialisation terminée avec succès!")

if __name__ == '__main__':
    init_system()