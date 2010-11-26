from django.shortcuts import render_to_response
from ldap import *

def index(request):
    return render_to_response('index.html')


#def ldapListUsers(ldap):
#    """List all ldap users"""
#    l = ldap.initialize("ad.dkfz-heidelberg.de")
#    l.simple_bind_s("OU=dkfz,DC=ad,DC=dkfz-heidelberg,DC=de", "logalvsa")
#
#
