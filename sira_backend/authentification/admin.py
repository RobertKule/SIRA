from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Role, UtilisateurRole

class CustomUserAdmin(UserAdmin):
    # 1. Supprimez la référence à username
    ordering = ('email',)  # Ordonner par email à la place
    
    # 2. Mettez à jour les fieldsets pour refléter vos champs
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'telephone')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # 3. Liste d'affichage
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    
    # 4. Ajoutez ces lignes si vous utilisez l'inscription dans l'admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

admin.site.register(Utilisateur, CustomUserAdmin)
admin.site.register(Role)
admin.site.register(UtilisateurRole)