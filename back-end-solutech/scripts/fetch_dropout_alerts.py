import requests, json

try:
    auth = requests.post('http://127.0.0.1:8000/api/auth/login/', json={'username':'GLOIRE','password':'gloire'})
    print('Auth Status:', auth.status_code)
    data = auth.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    if auth.status_code != 200:
        raise SystemExit(1)
    token = data.get('access')
    headers = {'Authorization': 'Bearer ' + token}
    r = requests.get('http://127.0.0.1:8000/api/pedagogie/presences/dropout-alerts/', headers=headers)
    print('GET Status:', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(r.text)
except Exception as e:
    print('Error:', e)
