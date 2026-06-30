from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.chef_dashboard, name='chef_dashboard'),
    path('mark/<int:event_id>/', views.mark_attendance, name='mark_attendance'),
      # NOUVEAU : Le dashboard analytique
    path('analytics/', views.admin_dashboard, name='admin_dashboard'), 
    path('serviteur/', views.serviteur_dashboard, name='serviteur_dashboard'),  # NOUVEAU
    path('search/', views.global_search, name='global_search'),  # NOUVEAU (voir étape 2)
    path('serviteur/add/', views.add_serviteur, name='add_serviteur'),
    path('serviteur/delete/<int:user_id>/', views.delete_serviteur, name='delete_serviteur'),
]