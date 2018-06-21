from django.conf.urls import url

from djvision.dashboard import views

urlpatterns = [
    url(
        r'^$',
        views.home, name='home'
    ),
]
