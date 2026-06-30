from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Colonnes affichées dans la liste
    list_display = ('username', 'prenom', 'nom', 'role', 'departement', 'is_active', 'is_staff')
    
    # Filtres dans la barre latérale droite
    list_filter = ('role', 'departement', 'is_staff', 'is_active')
    
    # Barre de recherche en haut
    search_fields = ('username', 'prenom', 'nom', 'email', 'telephone')
    
    # Organisation des champs dans le formulaire d'édition
    fieldsets = UserAdmin.fieldsets + (
        ('Informations ICC', {'fields': ('role', 'departement', 'telephone', 'adresse', 'profession')}),
    )
    
    # Organisation pour la création d'un utilisateur
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations ICC', {'fields': ('role', 'departement', 'prenom', 'nom')}),
    )