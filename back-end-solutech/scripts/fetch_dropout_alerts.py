import json
import sys

import requests

BASE_URL = 'http://127.0.0.1:8000'


def main() -> int:
    auth = requests.post(
        f'{BASE_URL}/api/auth/login/',
        json={'username': 'GLOIRE', 'password': 'gloire'},
        timeout=30,
    )
    print('Auth Status:', auth.status_code)
    try:
        data = auth.json()
    except ValueError:
        print('Réponse non JSON:', auth.text, file=sys.stderr)
        return 1
    print(json.dumps(data, indent=2, ensure_ascii=False))
    if auth.status_code != 200:
        return 1

    token = data.get('access')
    if not token:
        print("Aucun token 'access' dans la réponse", file=sys.stderr)
        return 1

    r = requests.get(
        f'{BASE_URL}/api/pedagogie/presences/dropout-alerts/',
        headers={'Authorization': 'Bearer ' + token},
        timeout=30,
    )
    print('GET Status:', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except ValueError:
        print(r.text)
    return 0 if r.ok else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except requests.RequestException as e:
        # Échec réseau : sortir en erreur pour ne pas masquer le problème en CI
        print('Erreur réseau:', e, file=sys.stderr)
        sys.exit(2)
