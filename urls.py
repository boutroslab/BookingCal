from django.conf.urls.defaults import *
from django.contrib import admin
from bookingCalPython import settings

admin.autodiscover()

urlpatterns = patterns('',
    (r'^booking/$', 'views.index'),
    (r'^admin/', include(admin.site.urls)),
    (r'^booking/admin/', include(admin.site.urls)),
    (r'^booking/kalendar/', include('ecalendar.urls')),
    (r'^booking/equipment/', 'views.equip'),
    (r'^booking/tour/', 'views.tour'),
    (r"^kalendar/delete/$", "ecalendar.views.delete"),
    (r"^kalendar/changeadd/$", "ecalendar.views.changeadd"),
    (r'^booking/static/(?P<path>.*)$', 'django.views.static.serve',
    {'document_root':     settings.MEDIA_ROOT}),

)
