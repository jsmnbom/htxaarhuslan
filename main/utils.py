import requests
from django.conf import settings
from sorl.thumbnail import get_thumbnail


def send_mobilepay_request(lan, profile, type, amount, id):
    url = ''
    if profile.photo:
        url = 'https://htxaarhuslan.dk' + get_thumbnail(profile.photo, '60x60', crop='center').url
    data = {
        'to': lan.payment_manager_id,
        'data': {
            'phone': '+45{}'.format(profile.phone),
            'amount': str(round(amount, 2)).replace('.', ','),
            'type': type,
            'username': profile.user.username,
            'id': id,
            'url': url
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key={}'.format(settings.GOOGLE_FIREBASE_AUTH_KEY)
    }
    print(data, headers)
    r = requests.post('https://fcm.googleapis.com/fcm/send', json=data, headers=headers)
    print(r.status_code)
    print(r.text)

