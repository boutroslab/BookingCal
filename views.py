from django.shortcuts import render_to_response
from ldap import *

def index(request):
    if request.session.get('ldapU_is_auth'):
        context=True
    else:
        context=False
    return render_to_response('index.html',dict(request=request,context=context))
