# -*- coding: utf-8 -*-
#
from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from djauth.decorators import portal_auth_required
from djvision.core.data import ProvisioningDetailRec
from djvision.dashboard.forms import DetailCreatedForm
from djzbar.utils.informix import get_session


@portal_auth_required(
    group='LIS', session_var='DJVISION_AUTH',
    redirect_url=reverse_lazy('access_denied'),
)
def home(request):
    error = None
    objects = None
    if request.method == 'POST':
        form = DetailCreatedForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            session = get_session(settings.INFORMIX_EARL)
            objects = session.query(ProvisioningDetailRec).filter(
                ProvisioningDetailRec.created_at >= data['created_at'],
            ).all()
    else:
        form = DetailCreatedForm()

    return render(
        request, 'dashboard/home.html', {
            'form': form, 'objects': objects, 'error': error,
        }
    )
