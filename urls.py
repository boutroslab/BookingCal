from django.conf.urls.defaults import *
from django.contrib import admin
from bookingCal import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^booking/$', 'bookingCal.views.index'),
    #(r'^admin/', include('django.contrib.admin.urls')) , 
    (r'^booking/admin/', include(admin.site.urls)),                  
    (r'^booking/kalendar/', include('ecalendar.urls')),               
    (r'^booking/equipment/', 'bookingCal.views.equip'),
                       
# (r'^static/(?P<path>.*)$', 'serve'),
    (r'^booking/static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root':    '/var/www/django/django_projects/bookingCal/static'}),
)
