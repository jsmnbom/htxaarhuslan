from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from main.sitemaps import MainSitemap, TilmeldSitemap
from main.views import ProfileAutocomplete
from . import views

sitemaps = {
    'main': MainSitemap,
    'tilmeld': TilmeldSitemap
}

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^info$', views.info, name='info'),
    url(r'^tilmeldliste$', views.tilmeldlist, name='tilmeldlist'),
    url(r'^tilmeld$', views.tilmeld, name='tilmeld'),
    url(r'^frameld$', views.frameld, name='frameld'),
    url(r'^turneringer$', views.tournament, name='turne'),
    url(r'^bruger/logind$', views.login_view, name='login'),
    url(r'^bruger/logud$', views.logout_view, name='logout'),
    url(r'^bruger/registreret$', views.registered, name='registered'),
    url(r'^bruger/registrer$', views.register, name='register'),
    url(r'^profil/$', views.profile, name='profile'),
    url(r'^profil/(?P<username>[\w.@+-]+)$', views.profile, name='profile'),
    url(r'^bruger/gammel$', views.legacy, name='legacy'),
    url(r'^bruger/needlogin$', views.needlogin, name='needlogin'),
    url(r'^privatliv$', views.policy, name='policy'),
    url(
        r'^autocomplete/profile/$',
        ProfileAutocomplete.as_view(),
        name='autocomplete-profile',
    ),
    # Change/forgot password stuff
    url(r'^bruger/kode/glemt/$',
        auth_views.password_reset,
        name="password_reset"),
    url(r'^bruger/kode/glemt/done/$',
        auth_views.password_reset_done,
        name="password_reset_done"),
    url(r'^bruger/kode/glemt/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        name="password_reset_confirm"),
    url(r'^bruger/kode/complete/$',
        auth_views.password_reset_complete,
        name="password_reset_complete"),
    url(r'^bruger/kode/skift$',
        auth_views.password_change,
        name="password_change"),
    url(r'^bruger/kode/skift/done$',
        auth_views.password_change_done,
        name="password_change_done"),
    # SEO AND ROBOTS STUFF
    url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name="robots"),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
