from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Interface admin sécurisée pour notre modèle User personnalisé"""
    
    model = User
    
    # Colonnes visibles dans la liste
    list_display = ('username', 'email', 'role', 'phone', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    ordering = ('username',)
    
    # 🔐 Formulaire d'AJOUT d'un utilisateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'phone', 'password1', 'password2'),
        }),
    )
    
    # 🛡️ Formulaire de MODIFICATION d'un utilisateur
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Informations MEPSA', {'fields': ('role', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Empêche la modification directe du mot de passe en clair
    readonly_fields = ('last_login', 'date_joined')