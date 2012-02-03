from django.conf.urls.defaults import *
from django.contrib import admin
from bookingCal import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^booking/$', 'bookingCal.views.index'),
    #(r'^admin/', include('django.contrib.admin.urls')) , 
    (r'^admin/', include(admin.site.urls)),
    (r'^kalendar/', include('ecalendar.urls')),
    (r'^equipment/', 'bookingCal.views.equip'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root':     settings.MEDIA_ROOT}),

)
