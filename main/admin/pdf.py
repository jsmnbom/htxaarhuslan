from collections import Counter
from pathlib import Path

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from main.models import get_next_lan


def table_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="borde.pdf"'

    width, height = A4[1], A4[0]

    c = canvas.Canvas(response, pagesize=(width, height))
    c.setCreator('HTXAarhusLAN.dk')

    tables = get_next_lan().parse_seats()[0]

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
            if c.stringWidth(text[:i]) > width * 0.8:
                text = text[:i] + '...'
                break
        c.drawCentredString(x, y, text)

    for seat, lp in pages:
        string(c, width / 2, height * 0.6, 250, seat)
        if lp is None:
            line1 = 'Denne plads er ikke reserveret.'
            line2 = 'Du kan derfor godt sætte dig her.'
        else:
            line1 = lp.profile.user.first_name
            line2 = '{}({})'.format(lp.profile.user.username, lp.profile.grade)
        string(c, width / 2, height * 0.48, 45, line1)
        string(c, width / 2, height * 0.36, 35, line2)

        c.setFontSize(12)
        c.drawString(width * 0.05, height * 0.12,
                     'Der kan være sket ændringer siden denne seddel blev printet.')
        c.drawString(width * 0.05, height * 0.1,
                     'Hvis du er i tvivl spørg et crew member eller check på htxaarhuslan.dk/tilmeld.')
        c.drawString(width * 0.05, height * 0.08,
                     'Ved ophold til lan skal du følge reglerne på htxaarhuslan.dk/info#regler.')

        c.drawImage(str(Path('main/static/main/img/logo.png')), width * 0.6, height * 0.07, width=width * 0.35,
                    preserveAspectRatio=True, anchor='sw', mask='auto')

        c.showPage()

    c.save()

    return response
