import json
import os

import requests

BASE_URL = os.environ.get('SOLUTECH_API_URL', 'http://127.0.0.1:8000').rstrip('/')
USERNAME = os.environ.get('SOLUTECH_ADMIN_USERNAME')
PASSWORD = os.environ.get('SOLUTECH_ADMIN_PASSWORD')

if not USERNAME or not PASSWORD:
    raise SystemExit(
        'Set SOLUTECH_ADMIN_USERNAME and SOLUTECH_ADMIN_PASSWORD (see back-end-solutech/.env.example).'
    )

try:
    auth = requests.post(
        f'{BASE_URL}/api/auth/login/',
        json={'username': USERNAME, 'password': PASSWORD},
        timeout=30,
    )
    print('Auth Status:', auth.status_code)
    data = auth.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    if auth.status_code != 200:
        raise SystemExit(1)
    token = data.get('access')
    headers = {'Authorization': 'Bearer ' + token}
    r = requests.get(
        f'{BASE_URL}/api/pedagogie/presences/dropout-alerts/',
        headers=headers,
        timeout=30,
    )
    print('GET Status:', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(r.text)
except Exception as e:
    print('Error:', e)
