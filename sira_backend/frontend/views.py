from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required,user_passes_test

from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from rest_framework_simplejwt.tokens import RefreshToken
from authentification.serializers import UserProfileSerializer

def home(request):
    """Page d'accueil publique"""
    return render(request, 'frontend/home.html')

def login_view(request):
    """Page de connexion personnalisée"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Optionnel : générer un token JWT pour usage futur (API)
            refresh = RefreshToken.for_user(user)
            request.session['access_token'] = str(refresh.access_token)
            request.session['refresh_token'] = str(refresh)

            messages.success(request, f"Bienvenue, {user.first_name} !")
            return redirect('dashboard')
        else:
            messages.error(request, "Identifiants incorrects.")
    else:
        form = AuthenticationForm()
    return render(request, 'frontend/login.html', {'form': form})

@login_required
def dashboard(request):
    """Tableau de bord personnalisé selon le rôle"""
    user = request.user
    serializer = UserProfileSerializer(user)
    profile_data = serializer.data

    context = {
        'user': user,
        'profile': profile_data,
    }

    # Rediriger vers le bon template selon le rôle
    profile_type = profile_data.get('profile_type')

    if profile_type == 'etudiant':
        return render(request, 'frontend/dashboard_etudiant.html', context)
    elif profile_type == 'enseignant':
        return render(request, 'frontend/dashboard_enseignant.html', context)
    elif user.is_staff or profile_type == 'admin':
        return render(request, 'frontend/dashboard_admin.html', context)
    else:
        messages.error(request, "Profil inconnu.")
        logout(request)
        return redirect('home')

def logout_view(request):
    """Déconnexion"""
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('home')

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_create_etudiant(request):
    return render(request, 'frontend/admin_create_etudiant.html')

@login_required
@user_passes_test(is_admin)
def admin_create_enseignant(request):
    return render(request, 'frontend/admin_create_enseignant.html')