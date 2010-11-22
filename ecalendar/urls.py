from django.conf.urls.defaults import *

urlpatterns = patterns('ecalendar.views',
    (r'^$', 'main'),
    (r"^month/(\d+)/(\d+)/(prev|next)/$", "month"),
    (r"^month/(\d+)/(\d+)/$", "month"),
    (r"^month$", "month"),
    (r"^day/(\d+)/(\d+)/(\d+)/$", "day"),
    (r"^event/(\d+)/$", "event"),

)
