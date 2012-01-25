from django.shortcuts import render_to_response
from ldap import *
from bookingCal.ecalendar.models import Equipment
from django.template import RequestContext


def index(request):
    if request.session.get('ldapU_is_auth'):
        context=True
    else:
        context=False
    return render_to_response('index.html',dict(request=request,context=context))
def equip(request):
    if request.session.get('ldapU_is_auth'):
        context=True
    else:
        context=False

    entries = Equipment.objects.filter(enabled=True).order_by('name')

    return render_to_response('equip.html',{'entries':entries,'context':context },context_instance=RequestContext(request))
