from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date, timedelta
from account.models import CustomUser, Department
from .models import ServiceEvent, Attendance


# --- DÉCORATEUR DE SÉCURITÉ STRICT ---
def chef_or_admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Vérification stricte du rôle
        if not hasattr(request.user, 'role') or request.user.role not in ['chef', 'admin']:
            messages.error(request, "🚫 Accès Interdit : Seuls les Chefs peuvent pointer.")
            return redirect('serviteur_dashboard')
        return view_func(request, *args, **kwargs)
    return login_required(_wrapped_view)

# --- VUE CHEF DASHBOARD ---@chef_or_admin_required
@chef_or_admin_required
def chef_dashboard(request):
    """Tableau de bord avec filtrage dynamique par département"""
    context = {}
    
    # 1. Récupérer tous les départements pour les boutons de filtre
    all_departments = Department.objects.all()
    context['all_departments'] = all_departments
    
    # 2. Détecter le département sélectionné via l'URL (?dept_id=X)
    selected_dept_id = request.GET.get('dept_id')
    current_dept = None
    
    if selected_dept_id:
        current_dept = Department.objects.filter(id=selected_dept_id).first()

    # 3. Déterminer quel département afficher selon le rôle
    if request.user.role == 'admin':
        # L'admin voit soit "Tous" (current_dept = None), soit le département filtré
        context['current_dept'] = current_dept
        display_dept = current_dept 
    else:
        # Le chef voit TOUJOURS son propre département, peu importe le filtre
        display_dept = request.user.departement
        context['current_dept'] = display_dept

    # 4. Calculer les statistiques en fonction du département affiché
    if display_dept:
        # Stats pour UN département spécifique
        total_membres = CustomUser.objects.filter(departement=display_dept, role='serviteur').count()
        
        # Liste complète avec toutes les infos (pour la section "Liste des Membres")
        liste_membres_complete = []
        membres_stats = []
        
        for membre in CustomUser.objects.filter(departement=display_dept, role='serviteur').order_by('nom', 'prenom'):
            m_total = Attendance.objects.filter(servant=membre).count()
            m_present = Attendance.objects.filter(servant=membre, status='present').count()
            m_absent = Attendance.objects.filter(servant=membre, status='absent').count()
            m_excuse = Attendance.objects.filter(servant=membre, status='excused').count()
            m_taux = round((m_present / m_total) * 100, 1) if m_total > 0 else 0
            
            # Pour la liste complète (triée par nom)
            liste_membres_complete.append({
                'membre': membre,
                'total': m_total,
                'presents': m_present,
                'absents': m_absent,
                'excuses': m_excuse,
                'taux': m_taux
            })
            
            # Pour le top 10 (trié par taux)
            membres_stats.append({
                'membre': membre, 
                'taux': m_taux
            })
        
        # Trier le top 10 par taux de présence (décroissant)
        membres_stats.sort(key=lambda x: x['taux'], reverse=True)
        
        # Alertes : membres avec moins de 50% de présence
        alertes = [m for m in membres_stats if m['taux'] < 50 and Attendance.objects.filter(servant=m['membre']).count() > 0]
        
        # Taux global du département
        total_pointages_dept = Attendance.objects.filter(department=display_dept).count()
        presents_dept = Attendance.objects.filter(department=display_dept, status='present').count()
        taux_presence = round((presents_dept / total_pointages_dept) * 100, 1) if total_pointages_dept > 0 else 0
        
        # Derniers pointages effectués dans ce département
        derniers_pointages = Attendance.objects.filter(
            department=display_dept
        ).order_by('-timestamp')[:5]
        
        context.update({
            'total_membres': total_membres,
            'taux_presence': taux_presence,
            'membres_stats': membres_stats[:10],
            'alertes': alertes,
            'derniers_pointages': derniers_pointages,
            'liste_membres_complete': liste_membres_complete,  # NOUVEAU : liste complète
            'user_department': display_dept
        })
    else:
        # Stats GLOBALES (Admin quand aucun filtre n'est actif)
        total_membres = CustomUser.objects.filter(role='serviteur').count()
        total_pointages = Attendance.objects.count()
        presents = Attendance.objects.filter(status='present').count()
        taux_presence = round((presents / total_pointages) * 100, 1) if total_pointages > 0 else 0
        
        # Liste complète de tous les serviteurs (pour l'admin)
        liste_membres_complete = []
        membres_stats = []
        
        for membre in CustomUser.objects.filter(role='serviteur').order_by('departement__name', 'nom', 'prenom'):
            m_total = Attendance.objects.filter(servant=membre).count()
            m_present = Attendance.objects.filter(servant=membre, status='present').count()
            m_absent = Attendance.objects.filter(servant=membre, status='absent').count()
            m_excuse = Attendance.objects.filter(servant=membre, status='excused').count()
            m_taux = round((m_present / m_total) * 100, 1) if m_total > 0 else 0
            
            liste_membres_complete.append({
                'membre': membre,
                'total': m_total,
                'presents': m_present,
                'absents': m_absent,
                'excuses': m_excuse,
                'taux': m_taux
            })
            
            membres_stats.append({
                'membre': membre, 
                'taux': m_taux
            })
        
        membres_stats.sort(key=lambda x: x['taux'], reverse=True)
        alertes = [m for m in membres_stats if m['taux'] < 50 and Attendance.objects.filter(servant=m['membre']).count() > 0]
        derniers_pointages = Attendance.objects.all().order_by('-timestamp')[:5]
        
        context.update({
            'total_membres': total_membres,
            'taux_presence': taux_presence,
            'membres_stats': membres_stats[:10],
            'alertes': alertes,
            'derniers_pointages': derniers_pointages,
            'liste_membres_complete': liste_membres_complete,
            'user_department': None
        })

    # 5. Départements à afficher dans les boutons "Pointer"
    if request.user.role == 'admin':
        context['departments'] = [current_dept] if current_dept else all_departments
    else:
        context['departments'] = [display_dept] if display_dept else []

    # 6. Événements (toujours les 5 derniers)
    context['events'] = ServiceEvent.objects.all().order_by('-date')[:5]
    
    
    # NOUVEAU : Récupérer le tout dernier événement pour le bouton "Pointer rapide"
    context['latest_event'] = ServiceEvent.objects.order_by('-date').first()
    
    
    return render(request, 'attendance/dashboard.html', context)






# --- VUE MARK ATTENDANCE (POINTAGE) ---
@login_required
def mark_attendance(request, event_id):
    # 🛑 BLOCAGE STRICT ET IMMÉDIAT (Sans décorateur)
    if request.user.role not in ['chef', 'admin']:
        messages.error(request, "🚫 ACCÈS INTERDIT : Seuls les chefs peuvent pointer.")
        return redirect('serviteur_dashboard')

    event = get_object_or_404(ServiceEvent, id=event_id)
    
    # Logique de département
    if request.user.role == 'admin':
        dept_id = request.GET.get('dept')
        if not dept_id:
            messages.error(request, "Admin: Veuillez sélectionner un département.")
            return redirect('chef_dashboard')
        department = get_object_or_404(Department, id=dept_id)
    else:
        # Le chef ne voit que son département
        department = request.user.departement
        if not department:
            messages.error(request, "Vous n'avez pas de département.")
            return redirect('serviteur_dashboard')
            
    members = CustomUser.objects.filter(departement=department, role='serviteur')
    
    if request.method == 'POST':
        for member in members:
            status = request.POST.get(f'status_{member.id}')
            if status:
                Attendance.objects.update_or_create(
                    servant=member, event=event,
                    defaults={'department': department, 'status': status, 'marked_by': request.user}
                )
        messages.success(request, f"✅ Présences pour {event.name} enregistrées !")
        return redirect('chef_dashboard')
        
    existing = {att.servant.id: att.status for att in Attendance.objects.filter(event=event, department=department)}
    members_with_status = [{'member': m, 'status': existing.get(m.id, '')} for m in members]
    
    return render(request, 'attendance/mark_attendance.html', {
        'event': event, 'department': department, 'members_with_status': members_with_status
    })
    
    
    
    

# --- VUE ADMIN DASHBOARD ---
@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('chef_dashboard')
    
    from django.db.models import Count, Q
    from datetime import timedelta

    # 1. KPIs de base
    total_serviteurs = CustomUser.objects.filter(role='serviteur').count()
    total_chefs = CustomUser.objects.filter(role='chef').count()
    total_pointages = Attendance.objects.count()
    presences_reelles = Attendance.objects.filter(status='present').count()
    taux_presence = round((presences_reelles / total_pointages) * 100, 1) if total_pointages > 0 else 0

    # 2. Répartition par département
    dept_stats = Department.objects.annotate(
        total_membres=Count('members', filter=Q(members__role='serviteur'))
    ).values('name', 'total_membres')
    labels_dept = [d['name'] for d in dept_stats]
    data_dept = [d['total_membres'] for d in dept_stats]

    # 3. Évolution sur les 5 derniers cultes
    derniers_events = ServiceEvent.objects.all().order_by('-date')[:5]
    labels_events = []
    data_events = []
    for event in derniers_events:
        labels_events.append(event.name[:15] + '...' if len(event.name) > 15 else event.name)
        presents = Attendance.objects.filter(event=event, status='present').count()
        data_events.append(presents)
    labels_events.reverse()
    data_events.reverse()

    # 4. Présence journalière (30 jours)
    today = date.today()
    labels_jour = []
    data_jour = []
    for i in range(29, -1, -1):
        jour = today - timedelta(days=i)
        labels_jour.append(jour.strftime('%d/%m'))
        presents = Attendance.objects.filter(timestamp__date=jour, status='present').count()
        data_jour.append(presents)

    # 5. Par jour de semaine
    jours_semaine = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
    data_jour_semaine = [0] * 7
    for i in range(30):
        jour = today - timedelta(days=i)
        weekday = jour.weekday()
        presents = Attendance.objects.filter(timestamp__date=jour, status='present').count()
        data_jour_semaine[weekday] += presents

    # 6. Comparatif et Top Départements (TRÈS IMPORTANT)
    dept_assiduite = []
    for dept in Department.objects.all():
        dept_total = Attendance.objects.filter(department=dept).count()
        dept_presents = Attendance.objects.filter(department=dept, status='present').count()
        dept_taux = round((dept_presents / dept_total) * 100, 1) if dept_total > 0 else 0
        dept_assiduite.append({'name': dept.name, 'taux': dept_taux})
    dept_assiduite.sort(key=lambda x: x['taux'], reverse=True)
    
    top_depts = dept_assiduite[:5]
    labels_comparatif = [d['name'] for d in dept_assiduite]
    data_comparatif = [d['taux'] for d in dept_assiduite]

    # 7. Top Serviteurs
    serviteurs_assidus = []
    for serv in CustomUser.objects.filter(role='serviteur'):
        serv_total = Attendance.objects.filter(servant=serv).count()
        serv_presents = Attendance.objects.filter(servant=serv, status='present').count()
        serv_taux = round((serv_presents / serv_total) * 100, 1) if serv_total > 0 else 0
        serviteurs_assidus.append({
            'nom': f"{serv.prenom} {serv.nom}",
            'dept': serv.departement.name if serv.departement else '-',
            'taux': serv_taux
        })
    serviteurs_assidus.sort(key=lambda x: x['taux'], reverse=True)
    top_serviteurs = serviteurs_assidus[:10]

    context = {
        'total_serviteurs': total_serviteurs,
        'total_chefs': total_chefs,
        'taux_presence': taux_presence,
        'labels_dept': labels_dept,
        'data_dept': data_dept,
        'labels_events': labels_events,
        'data_events': data_events,
        'labels_jour': labels_jour,
        'data_jour': data_jour,
        'jours_semaine': jours_semaine,
        'data_jour_semaine': data_jour_semaine,
        'labels_comparatif': labels_comparatif,
        'data_comparatif': data_comparatif,
        'top_depts': top_depts,
        'top_serviteurs': top_serviteurs,
    }
    return render(request, 'attendance/admin_dashboard.html', context)

# --- VUE SERVITEUR DASHBOARD ---
@login_required
def serviteur_dashboard(request):
    mes_presences = Attendance.objects.filter(servant=request.user).order_by('-event__date')[:20]
    total_evenements = Attendance.objects.filter(servant=request.user).count()
    total_presents = Attendance.objects.filter(servant=request.user, status='present').count()
    taux_presence = round((total_presents / total_evenements) * 100, 1) if total_evenements > 0 else 0
    
    prochains_events = ServiceEvent.objects.filter(date__gte=timezone.now().date()).order_by('date')[:5]
    
    # Calcul du classement
    position = 0
    if request.user.departement:
        membres_dept = CustomUser.objects.filter(departement=request.user.departement, role='serviteur')
        classement = []
        for m in membres_dept:
            t = Attendance.objects.filter(servant=m).count()
            p = Attendance.objects.filter(servant=m, status='present').count()
            classement.append({'id': m.id, 'taux': round((p/t)*100, 1) if t > 0 else 0})
        classement.sort(key=lambda x: x['taux'], reverse=True)
        position = next((i+1 for i, c in enumerate(classement) if c['id'] == request.user.id), 0)

    return render(request, 'attendance/serviteur_dashboard.html', {
        'mes_presences': mes_presences, 'total_evenements': total_evenements,
        'total_presents': total_presents, 'taux_presence': taux_presence,
        'prochains_events': prochains_events, 'position': position,
        'total_membres_dept': len(membres_dept) if request.user.departement else 0
    })

# --- VUE RECHERCHE ---
@login_required
def global_search(request):
    query = request.GET.get('q', '').strip()
    results = {'users': [], 'events': [], 'departments': []}
    if query:
        if request.user.role == 'admin':
            results['users'] = CustomUser.objects.filter(Q(prenom__icontains=query) | Q(nom__icontains=query))[:10]
            results['departments'] = Department.objects.filter(name__icontains=query)[:10]
        else:
            results['users'] = CustomUser.objects.filter(departement=request.user.departement).filter(Q(prenom__icontains=query) | Q(nom__icontains=query))[:10]
        results['events'] = ServiceEvent.objects.filter(name__icontains=query)[:10]
    return render(request, 'attendance/search_results.html', {'query': query, 'results': results})





@chef_or_admin_required
def add_serviteur(request):
    """Permet au chef d'ajouter un serviteur dans son département"""
    
    # Déterminer le département du chef
    if request.user.role == 'admin':
        # L'admin choisit le département via un paramètre URL
        dept_id = request.GET.get('dept') or request.POST.get('departement')
        if dept_id:
            department = get_object_or_404(Department, id=dept_id)
        else:
            departments = Department.objects.all()
            return render(request, 'attendance/add_serviteur.html', {
                'departments': departments,
                'mode': 'choose_dept'
            })
    else:
        department = request.user.departement
        if not department:
            messages.error(request, "Vous n'avez pas de département assigné.")
            return redirect('chef_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        nom = request.POST.get('nom', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        profession = request.POST.get('profession', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        # Validations
        errors = []
        if not username:
            errors.append("Le nom d'utilisateur est obligatoire.")
        if not prenom:
            errors.append("Le prénom est obligatoire.")
        if not nom:
            errors.append("Le nom est obligatoire.")
        if not password or len(password) < 4:
            errors.append("Le mot de passe doit contenir au moins 4 caractères.")
        if CustomUser.objects.filter(username=username).exists():
            errors.append(f"Le nom d'utilisateur '{username}' est déjà utilisé.")
        if email and CustomUser.objects.filter(email=email).exists():
            errors.append(f"L'email '{email}' est déjà utilisé.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'attendance/add_serviteur.html', {
                'department': department,
                'form_data': request.POST
            })

        # Création du serviteur
        user = CustomUser(
            username=username,
            prenom=prenom,
            nom=nom,
            telephone=telephone,
            profession=profession,
            adresse=adresse,
            email=email,
            role='serviteur',
            departement=department,
            is_active=True
        )
        user.set_password(password)
        user.save()

        messages.success(request, f"✅ {prenom} {nom} a été ajouté avec succès dans {department.name} !")
        return redirect('chef_dashboard')

    return render(request, 'attendance/add_serviteur.html', {
        'department': department
    })


@chef_or_admin_required
def delete_serviteur(request, user_id):
    """Permet au chef de supprimer un serviteur de son département"""
    serviteur = get_object_or_404(CustomUser, id=user_id)
    
    # Sécurité : le chef ne peut supprimer que les serviteurs de son département
    if request.user.role != 'admin' and serviteur.departement != request.user.departement:
        messages.error(request, "Vous ne pouvez pas supprimer un serviteur d'un autre département.")
        return redirect('chef_dashboard')
    
    if serviteur.role != 'serviteur':
        messages.error(request, "Vous ne pouvez supprimer que des serviteurs.")
        return redirect('chef_dashboard')

    if request.method == 'POST':
        nom_complet = f"{serviteur.prenom} {serviteur.nom}"
        serviteur.delete()
        messages.success(request, f"✅ {nom_complet} a été supprimé avec succès.")
        return redirect('chef_dashboard')

    return render(request, 'attendance/delete_serviteur.html', {
        'serviteur': serviteur
    })