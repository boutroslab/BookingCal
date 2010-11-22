from django.conf.urls.defaults import *

from bookingCal.cal.controller import CalendarController
from bookingCal.cal.models import Event

## calendar view
urlpatterns = patterns('cal.views',
    (r'^view/.*$', 'view'),
    (r'^upd/.*$', 'updEvent'),
    (r'^add/.*$', 'addEvent'),
    (r'^del/.*$', 'delEvent'),
    (r'^.*$', 'view'),
)

