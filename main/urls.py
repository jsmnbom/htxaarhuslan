import challonge
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from main.sitemaps import MainSitemap, TilmeldSitemap
from main.views import ProfileAutocomplete
from . import views

sitemaps = {
    'main': MainSitemap,
    'tilmeld': TilmeldSitemap
}

urlpatterns = [
    path('', views.index, name='index'),
    path('info/', views.info, name='info'),
    path('tilmeldliste/', views.tilmeldlist, name='tilmeldlist'),
    path('tilmeld/', views.tilmeld, name='tilmeld'),
    path('frameld/', views.frameld, name='frameld'),
    path('turnering/', views.tournaments, name='tournaments'),
    path('turnering/<game>/<lan_id>/<name>/', views.tournament, name='tournament'),
    path('bruger/logind/', views.login_view, name='login'),
    path('bruger/logud/', views.logout_view, name='logout'),
    path('bruger/registreret/', views.registered, name='registered'),
    path('bruger/registrer/', views.register, name='register'),
    path('profil/', views.profile, name='profile'),
    path('profil/<username>/', views.profile, name='profile'),
    path('bruger/gammel/', views.legacy, name='legacy'),
    path('bruger/needlogin/', views.needlogin, name='needlogin'),
    path('privatliv/', views.policy, name='policy'),
    path('calendar/<feed_name>.json', views.calendar, name='calendar'),
    path('mad/', views.food, name='food'),
    path('event/<event_id>/', views.event, name='event'),
    # path('betaling/<service>/<type>/<id>/',
    #      views.payment,
    #      name='send_payment_request'),

    # Autocompletes
    path('autocomplete/profile/',
         ProfileAutocomplete.as_view(),
         name='autocomplete-profile'),

    # Change/forgot password stuff
    path('bruger/kode/glemt/',
         auth_views.PasswordResetView.as_view(),
         name="password_reset"),
    path('bruger/kode/glemt/done/',
         auth_views.PasswordResetDoneView.as_view(),
         name="password_reset_done"),
    path('bruger/kode/glemt/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
    path('bruger/kode/complete/',
         auth_views.PasswordResetCompleteView.as_view(),
         name="password_reset_complete"),
    path('bruger/kode/skift',
         auth_views.PasswordChangeView.as_view(),
         name="password_change"),
    path('bruger/kode/skift/done',
         auth_views.PasswordChangeDoneView.as_view(),
         name="password_change_done"),

    # SEO AND ROBOTS STUFF
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name="robots"),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Other links
    path('discord', RedirectView.as_view(url="https://discord.gg/3DJaNFY", permanent=False), name='discord'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.CHALLONGE_USER and settings.CHALLONGE_API_KEY:
    challonge.set_credentials(settings.CHALLONGE_USER, settings.CHALLONGE_API_KEY)
