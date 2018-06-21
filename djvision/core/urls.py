from django.conf.urls import include, url

from django.contrib import admin

admin.autodiscover()

handler404 = 'djtools.views.errors.four_oh_four_error'
handler500 = 'djtools.views.errors.server_error'


urlpatterns = [
    url(
        r'^admin/', include(admin.site.urls)
    ),
    # dashboard
    url(
        r'^dashboard/', include('djvision.dashboard.urls')
    )
]
