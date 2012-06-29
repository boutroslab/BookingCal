## Django settings for bookingCal project.
import os
import sys
import logging
# put the Django project on sys.path
path = '/var/www/django/django_projects/bookingCal'
if path not in sys.path:
    sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'bookingCal.settings'



#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()

DEBUG = True
TEMPLATE_DEBUG = DEBUG


ADMINS = (
           ('B110-IT', 'b110-it@dkfz.de'),
          )

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'buchung_django', # Or path to database file if using sqlite3.
        'USER': 'django', # Not used with sqlite3.
        'PASSWORD': 'dj4n60', # Not used with sqlite3.
        'HOST': 'b110-dbserve', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}



# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.

#TIME_ZONE = 'America/Chicago'
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'de'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT =path+ '/static'
#MEDIA_ROOT='/Users/Yannic/PycharmProjects/bookingCal/static/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
#MEDIA_URL = '/media/'

# URL prefix for bookingCal media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".

#ADMIN_MEDIA_PREFIX = '/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'eu_2&go98qy@ad&(g^!hggtt=i#+hjg48*-u$)0)+a-8!6c=b-'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    #     'django.template.loaders.eggs.Loader',
                    )

MIDDLEWARE_CLASSES = (
                      'django.middleware.common.CommonMiddleware',
                      'django.contrib.sessions.middleware.SessionMiddleware',
                      'django.middleware.csrf.CsrfViewMiddleware',
                      'django.contrib.auth.middleware.AuthenticationMiddleware',
                      'django.contrib.messages.middleware.MessageMiddleware',
                      )

ROOT_URLCONF = 'bookingCal.urls'

TEMPLATE_DIRS = (
                 # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
                 # Always use forward slashes, even on Windows.
                 # Don't forget to use absolute paths, not relative paths.
		 '/var/www/django/django_templates' 
	         #'templates'
                 )

INSTALLED_APPS = (
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.sites',
                  'django.contrib.messages',
                  'django.contrib.admin',
                  'bookingCal.ecalendar'
             )
SESSION_COOKIE_AGE = 86400
