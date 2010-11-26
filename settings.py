# Django settings for helloWorld project.
from django_auth_ldap.config import LDAPSearch  , GroupOfNamesType


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
          # ('Your Name', 'your_email@domain.com'),
          )

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'book', # Or path to database file if using sqlite3.
        'USER': 'test', # Not used with sqlite3.
        'PASSWORD': 'test', # Not used with sqlite3.
        'HOST': 'localhost', # Set to empty string for localhost. Not used with sqlite3.
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
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = "/Users/Yannic/PycharmProjects/bookingCal/static"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/main/'

# URL prefix for bookingCal media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".

ADMIN_MEDIA_PREFIX = '/Users/Yannic/PycharmProjects/bookingCal/static/admin/'

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
                 "/Users/Yannic/PycharmProjects/bookingCal/templates"
                 )

INSTALLED_APPS = (
                  'django.contrib.auth',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.sites',
                  'django.contrib.messages',
                  'django.contrib.admin',
                  'bookingCal.ecalendar',

              )

#AD_DNS_NAME='ad.dkfz-heidelberg.de'
# If using non-SSL use these
#AD_LDAP_PORT=389
#AD_LDAP_URL='ldap://%s:%s' %
#(AD_DNS_NAME,AD_LDAP_PORT)
# If using SSL use these:
#AD_LDAP_PORT=636
#AD_LDAP_URL='ldaps://%s:%s' % (AD_DNS_NAME,AD_LDAP_PORT)
#AD_SEARCH_DN='dc=b110,dc=net,dc=com'
#AD_NT4_DOMAIN='YOURDOMAIN'
#AD_SEARCH_FIELDS= ['mail','givenName','sn','sAMAccountName','memberOf']
#AD_MEMBERSHIP_REQ=['Group_Required','Alternative_Group']
#AD_CERT_FILE='/path/to/your/cert.txt'
#AUTHENTICATION_BACKENDS = (
#    'reviewboard.accounts.backends.ActiveDirectoryGroupMembershipSSLBackend',
#    'django.contrib.auth.backends.ModelBackend'
#)
#AD_DEBUG=True
#AD_DEBUG_FILE='/Users/Yannic/PycharmProjects/bookingCal/static/ldap.debug'


#AUTH_LDAP_SERVER_URI="ad.dkfz-heidelberg.de"
#LDAPDB_BIND_DN="OU=dkfz,DC=ad,DC=dkfz-heidelberg,DC=de"
#LDAPDB_BIND_PASSWORD="logalvsa"



#import ldap
#from django.contrib.auth.contrib.ldap.config import LDAPSearch, GroupOfNamesType
#
## Baseline configuration.
#AUTH_LDAP_SERVER_URI = "ad.dkfz-heidelberg.de"
#AUTH_LDAP_BIND_DN = "OU=dkfz,DC=ad,DC=dkfz-heidelberg,DC=de"
#AUTH_LDAP_BIND_PASSWORD = "logalvsa"
#AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=com",
#ldap.SCOPE_SUBTREE, "(uid=%(user)s)") # or perhaps:
#
## AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"
## Set up the basic group parameters.
#
#AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=django,ou=groups,dc=example,dc=com",
#                                    ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
#)
#AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")
#
## Only users in this group can log in.
#
#AUTH_LDAP_REQUIRE_GROUP = "cn=enabled,ou=django,ou=groups,dc=example,dc=com"
#
## Populate the Django user from the LDAP directory.
#
#AUTH_LDAP_USER_ATTR_MAP = { "first_name": "givenName",
#        "last_name": "sn", "email": "mail"
#}
#AUTH_LDAP_PROFILE_ATTR_MAP = {
#        "employee_number": "employeeNumber"
#}
#AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#    "is_active": "cn=active,ou=django,ou=groups,dc=example,dc=com",
#    "is_staff": "cn=staff,ou=django,ou=groups,dc=example,dc=com",
#    "is_superuser": "cn=superuser,ou=django,ou=groups,dc=example,dc=com"
#}
## This is the default, but I like to be explicit.
#
#AUTH_LDAP_ALWAYS_UPDATE_USER = True # Use LDAP group membership to calculate group permissions.
#AUTH_LDAP_FIND_GROUP_PERMS = True
#
## Cache group memberships for an hour to minimize LDAP traffic
#AUTH_LDAP_CACHE_GROUPS = True
#AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600
#
## Keep ModelBackend around for per-user permissions and maybe a local # superuser.
#AUTHENTICATION_BACKENDS = (
#    'django.contrib.auth.contrib.ldap.backend.LDAPBackend',
#    'django.contrib.auth.backends.ModelBackend',
#)


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.contrib.ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)


# Baseline configuration.
AUTH_LDAP_SERVER_URI = "ad.dkfz-heidelberg.de"
AUTH_LDAP_BIND_DN = "OU=dkfz,DC=ad,DC=dkfz-heidelberg,DC=de"
AUTH_LDAP_BIND_PASSWORD = "logalvsa"
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=com",ldap.SCOPE_SUBTREE, "(uid=%(user)s)") # or perhaps:

