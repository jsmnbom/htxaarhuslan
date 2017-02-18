from django.conf.urls import url
from django.contrib import admin

from main.admin.pdf import table_pdf


def get_admin_urls(urls):
    def get_urls():
        my_urls = [
            url(r'^pdf/bordkort.pdf/$', admin.site.admin_view(table_pdf))
        ]
        return my_urls + urls

    return get_urls


admin_urls = get_admin_urls(admin.site.get_urls())
admin.site.get_urls = admin_urls
