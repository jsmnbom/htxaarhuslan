from collections import Counter
from pathlib import Path

from django.http import HttpResponse, Http404
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from main.models import Lan

H, W = A4  # Landscape


def table_pdf(request, lan_id):
    try:
        lan = Lan.objects.get(id=lan_id)
    except Lan.DoesNotExist:
        raise Http404

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Bordkort {}.pdf"'.format(lan.name)

    c = canvas.Canvas(response, pagesize=(W, H))
    c.setCreator('HTXAarhusLAN.dk')

    tables = lan.parse_seats()[0]
    origins = {}
    lengths = Counter(), Counter()

    for y, table in enumerate(tables):
        for x, seat in enumerate(table):
            if seat[0] is not None:
                if seat[0][0] not in origins:
                    origins[seat[0][0]] = (x, y)
                if lengths[0][seat[0][0]] < x - origins[seat[0][0]][0]:
                    lengths[0][seat[0][0]] = x - origins[seat[0][0]][0]
                if lengths[1][seat[0][0]] < y - origins[seat[0][0]][1]:
                    lengths[1][seat[0][0]] = y - origins[seat[0][0]][1]

    horizontal = {table: lengths[0][table] > lengths[1][table] for table in lengths[0]}
    pages = {seat[0]: seat[1] for table in tables for seat in table if seat[0] is not None}

    def sort(page):
        if horizontal[page[0][0]]:
            return page[0]
        else:
            n = int(page[0][1:])
            return page[0][0] + ('Z' if n % 2 == 0 else '') + str(n).zfill(2)

    pages = sorted(pages.items(), key=sort)

    def string(c, x, y, size, text):
        c.setFontSize(size)
        for i in range(len(text)):
            if c.stringWidth(text[:i]) > W * 0.8:
                text = text[:i] + '...'
                break
        c.drawCentredString(x, y, text)

    for seat, lp in pages:
        string(c, W / 2, H * 0.6, 250, seat)
        if lp is None:
            line1 = 'Denne plads er ikke reserveret.'
            line2 = 'Du kan derfor godt sætte dig her.'
        else:
            line1 = lp.profile.user.first_name
            line2 = '{}({})'.format(lp.profile.user.username, lp.profile.grade)
        string(c, W / 2, H * 0.48, 45, line1)
        string(c, W / 2, H * 0.36, 35, line2)

        c.setFontSize(12)
        lines = [
            'Husk at tilmelde dig vores discord server på linket: https://discord.gg/3DJaNFY',
            'Det er her der vil komme løbende updateringer under LANet.',
            'Der kan være sket ændringer siden denne seddel blev printet.',
            'Hvis du er i tvivl spørg et crew member eller check på htxaarhuslan.dk/tilmeld.',
            'Ved ophold til lan skal du følge reglerne på htxaarhuslan.dk/info#regler.'
        ]
        for i, line in enumerate(lines):
            c.drawString(W * 0.05, H * (0.06 + 0.02 * (len(lines) - i)), line)

        c.drawImage(str(Path('main/static/main/img/logo.png')), W * 0.75, H * 0.07, width=W * 0.2,
                    preserveAspectRatio=True, anchor='sw', mask='auto')

        c.showPage()

    c.save()

    return response
