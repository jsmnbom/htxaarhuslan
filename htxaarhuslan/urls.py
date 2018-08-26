"""htxaarhuslan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from rest_framework import routers

from main.api import FoodViewSet, LanProfileViewSet

router = routers.DefaultRouter()
router.register(r'food', FoodViewSet)
router.register(r'lanprofile', LanProfileViewSet)

urlpatterns = [
    path('', include('main.urls')),
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    path('admin/', admin.site.urls),
    path('api/auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

admin.site.site_header = 'HAL administation'
admin.site.site_title = 'HTX Aarhus LAN administation'

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
