from django.shortcuts import render_to_response
from ldap import *
from ecalendar.models import *
from django.template import RequestContext
from django.contrib.auth.models import User


def index(request):
    if request.session.get('ldapU_is_auth'):
        context=True
    else:
        context=False    
    return render_to_response('index.html',dict(request=request,context=context), context_instance=RequestContext(request))
def tour(request):
    if request.session.get('ldapU_is_auth'):
        context=True
    else:
        context=False    
    return render_to_response('tour.html',dict(request=request,context=context), context_instance=RequestContext(request))

def equip(request):
    if request.session.get('ldapU_is_auth'):
        context=True
    else:
        context=False

    entries = Equipment.objects.filter(enabled=True).order_by('name')

    return render_to_response('equip.html',{'entries':entries,'context':context },context_instance=RequestContext(request))
