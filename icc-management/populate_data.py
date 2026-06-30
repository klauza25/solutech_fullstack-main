# populate_data.py
import os
import django
from datetime import date, timedelta
from random import choice

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from account.models import CustomUser, Department
from attendance.models import ServiceEvent, Attendance

print("🌱 Création des départements...")
departments_data = [
    "Louange & Adoration",
    "Protocole & Accueil",
    "Multimédia",
    "Intercession",
    "Jeunesse",
    "Enfants",
    "Diaconat",
    "Communication",
]

departments = []
for name in departments_data:
    dept, created = Department.objects.get_or_create(name=name)
    departments.append(dept)
    if created:
        print(f"  ✅ {name}")

print("\n👥 Création des chefs de département...")
chefs_data = [
    ("marie_louange", "Marie", "Kabongo", "0612345601", "Chantre", departments[0]),
    ("jean_proto", "Jean", "Moukoko", "0612345602", "Coordinateur", departments[1]),
    ("paul_media", "Paul", "Ngoma", "0612345603", "Ingénieur Son", departments[2]),
    ("grace_pri", "Grâce", "Banzouzi", "0612345604", "Pasteur", departments[3]),
    ("david_jeune", "David", "Itoua", "0612345605", "Responsable Jeunesse", departments[4]),
]

chefs = []
for username, prenom, nom, tel, prof, dept in chefs_data:
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            'prenom': prenom,
            'nom': nom,
            'telephone': tel,
            'profession': prof,
            'role': 'chef',
            'departement': dept,
            'is_active': True,
            'is_staff': True,
        }
    )
    if created:
        user.set_password("password123")
        user.save()
        chefs.append(user)
        print(f"  ✅ {prenom} {nom} ({dept.name})")

print("\n🙏 Création des serviteurs...")
serviteurs_data = [
    # Louange (5 serviteurs)
    ("samba", "Samba", "Japhet", "0610000001", "Ingénieur Logiciel", departments[0]),
    ("ruth", "Ruth", "Mbongi", "0610000002", "Étudiante", departments[0]),
    ("josue", "Josué", "Lekoundzou", "0610000003", "Comptable", departments[0]),
    ("esther", "Esther", "Nkaya", "0610000004", "Enseignante", departments[0]),
    ("daniel", "Daniel", "Ongagna", "0610000005", "Développeur", departments[0]),
    
    # Protocole (4 serviteurs)
    ("pierre", "Pierre", "Mavoungou", "0610000006", "Commerçant", departments[1]),
    ("marthe", "Marthe", "Ibounda", "0610000007", "Infirmière", departments[1]),
    ("jacques", "Jacques", "Ngouabi", "0610000008", "Chauffeur", departments[1]),
    ("sarah", "Sarah", "Makaya", "0610000009", "Secrétaire", departments[1]),
    
    # Multimédia (3 serviteurs)
    ("lucas", "Lucas", "Bemba", "0610000010", "Vidéaste", departments[2]),
    ("lea", "Léa", "Koumba", "0610000011", "Graphiste", departments[2]),
    ("matthieu", "Matthieu", "Loubaki", "0610000012", "Technicien IT", departments[2]),
    
    # Intercession (4 serviteurs)
    ("anna", "Anna", "Mfoutou", "0610000013", "Médecin", departments[3]),
    ("paul2", "Paul", "Nzassi", "0610000014", "Pasteur", departments[3]),
    ("deborah", "Déborah", "Iloki", "0610000015", "Avocate", departments[3]),
    ("samuel", "Samuel", "Moussavou", "0610000016", "Enseignant", departments[3]),
    
    # Jeunesse (5 serviteurs)
    ("tim", "Timothée", "Bouity", "0610000017", "Étudiant", departments[4]),
    ("priscilla", "Priscilla", "Voua", "0610000018", "Étudiante", departments[4]),
    ("silas", "Silas", "Moussonda", "0610000019", "Jeune Pro", departments[4]),
    ("lydie", "Lydie", "Ndinga", "0610000020", "Étudiante", departments[4]),
    ("barnabe", "Barnabé", "Obambi", "0610000021", "Étudiant", departments[4]),
]

serviteurs = []
for username, prenom, nom, tel, prof, dept in serviteurs_data:
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            'prenom': prenom,
            'nom': nom,
            'telephone': tel,
            'profession': prof,
            'role': 'serviteur',
            'departement': dept,
            'is_active': True,
        }
    )
    if created:
        user.set_password("password123")
        user.save()
        serviteurs.append(user)
        print(f"  ✅ {prenom} {nom} ({dept.name})")

print("\n📅 Création des événements...")
today = date.today()
events_data = [
    ("Culte du Dimanche", "culte_dimanche", today - timedelta(days=28)),
    ("Culte du Dimanche", "culte_dimanche", today - timedelta(days=21)),
    ("Culte du Dimanche", "culte_dimanche", today - timedelta(days=14)),
    ("Culte du Dimanche", "culte_dimanche", today - timedelta(days=7)),
    ("Culte du Dimanche", "culte_dimanche", today),
    ("Veillée de Prière", "veillee", today - timedelta(days=10)),
    ("Réunion Jeunesse", "reunion_dept", today - timedelta(days=5)),
]

events = []
for name, etype, edate in events_data:
    event, created = ServiceEvent.objects.get_or_create(
        name=f"{name} - {edate}",
        defaults={'event_type': etype, 'date': edate}
    )
    events.append(event)
    if created:
        print(f"  ✅ {event.name}")

print("\n📊 Création des présences (cela peut prendre quelques secondes)...")
count = 0
for event in events:
    for serviteur in serviteurs:
        # 85% de présence en moyenne
        if choice([True] * 17 + [False] * 3):  # 85% de chance d'être présent
            status = choice(['present'] * 9 + ['excused'])  # 90% présent, 10% excusé
        else:
            status = 'absent'
        
        Attendance.objects.get_or_create(
            servant=serviteur,
            event=event,
            defaults={
                'department': serviteur.departement,
                'status': status,
                'marked_by': choice(chefs) if chefs else None
            }
        )
        count += 1

print(f"  ✅ {count} présences créées")

print("\n🎉 TERMINÉ !")
print("=" * 50)
print("📋 Comptes créés :")
print("  👑 Admin : Utilise 'createsuperuser' (déjà créé)")
print("  👔 Chefs : marie_louange, jean_proto, paul_media, grace_pri, david_jeune")
print("  🙏 Serviteurs : samba, ruth, josue, esther, daniel, etc.")
print("  🔑 Mot de passe pour tous : password123")
print("=" * 50)