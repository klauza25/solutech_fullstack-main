from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


admin.site.site_header = "ICC Management"          # Remplace "Administration de Django"
admin.site.site_title = "ICC Admin Portal"         # Remplace "Site d’administration" (onglet du navigateur)
admin.site.index_title = "Gestion de l'église ICC" # Remplace "Site d’administration" (au-dessus des listes)


def home_redirect(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Redirection intelligente selon le rôle
    if request.user.role == 'admin':
        return redirect('chef_dashboard')  # Admin voit aussi le dashboard chef
    elif request.user.role == 'chef':
        return redirect('chef_dashboard')
    else:  # serviteur
        return redirect('serviteur_dashboard')

urlpatterns = [
    path('gestion-icc/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('attendance/', include('attendance.urls')),
    path('', home_redirect, name='home'),
    
    
]