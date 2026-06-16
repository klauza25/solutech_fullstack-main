import os
import sys
from pathlib import Path
import django
from datetime import date

# Ensure project root is on PYTHONPATH so Django can import the settings package
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soluTech.settings')
django.setup()

from comptes.models import User
from ecoles.models import Ecole, Classe
from eleves.models import Eleve, LienFamille
from pedagogie.models import Matiere, Evaluation, Presence
from django.utils import timezone

print('Seeding database...')

# 1. Ecole
ecole, _ = Ecole.objects.get_or_create(
    code_mepsa='TEST-001',
    defaults={
        'nom': 'Lycée Test',
        'type': 'LYCEE',
        'cycles': 'LYCEE',
        'region': 'Brazzaville',
        'telephone': '+242000000',
        'email': 'contact@test.edu',
    }
)
print('Ecole:', ecole)

# 2. Classe
classe, _ = Classe.objects.get_or_create(
    nom='6ème A',
    ecole=ecole,
    defaults={'niveau': '6EME'}
)
print('Classe:', classe)

# 3. Users
admin, _ = User.objects.get_or_create(username='GLOIRE', defaults={'email':'admin@test.local','role':'ADMIN','is_staff':True})
admin.set_password('gloire')
admin.save()

teacher, _ = User.objects.get_or_create(username='prof1', defaults={'email':'prof1@test.local','role':'PROFESSEUR','ecole':ecole})
teacher.set_password('prof1')
teacher.save()

parent, _ = User.objects.get_or_create(username='parent1', defaults={'email':'parent1@test.local','role':'PARENT'})
parent.set_password('parent1')
parent.save()

print('Users created: admin, teacher, parent')

# 4. Eleve
eleve, created = Eleve.objects.get_or_create(
    matricule_mepsa='M2026-TEST-001',
    defaults={
        'nom': 'DOE',
        'prenom': 'John',
        'genre': 'M',
        'date_naissance': date(2012, 6, 1),
        'ecole': ecole,
        'classe_actuelle': classe,
    }
)
print('Eleve:', eleve)

# Link parent to eleve
LienFamille.objects.get_or_create(eleve=eleve, parent=parent, defaults={'type_lien':'PERE','est_responsable_financier':True})
print('Linked parent to eleve')

# 5. Matieres
math, _ = Matiere.objects.get_or_create(code='MATH', defaults={'nom':'Mathématiques','coefficient_defaut':2.0})
fr, _ = Matiere.objects.get_or_create(code='FR', defaults={'nom':'Français','coefficient_defaut':1.5})
print('Matieres:', math, fr)

# 6. Evaluation
Evaluation.objects.get_or_create(
    eleve=eleve,
    matiere=math,
    classe=classe,
    trimestre=1,
    type_eval='INT',
    defaults={
        'coefficient': 1.0,
        'note_sur_20': 14.5,
        'date_eval': timezone.now().date(),
        'est_validee': False,
    }
)
print('Evaluation created')

# 7. Presence
Presence.objects.get_or_create(
    eleve=eleve,
    date=date(2026,5,12),
    defaults={
        'classe': classe,
        'trimestre': 2,
        'statut': 'ABS',
        'justification': '',
        'recorded_by': admin,
    }
)
print('Presence created')

print('Seeding complete.')
