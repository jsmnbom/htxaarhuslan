"""
Django settings for htxaarhuslan project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os


def env_var(key, default=None):
    """Retrieves env vars and makes Python boolean replacements"""
    val = os.environ.get(key, default)
    if val == 'True':
        val = True
    elif val == 'False':
        val = False
    return val

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env_var('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_var('DEBUG', False)
THUMBNAIL_DEBUG = DEBUG

ALLOWED_HOSTS = env_var('ALLOWED_HOSTS', '').split(',')
if ALLOWED_HOSTS == ['']:
    ALLOWED_HOSTS = []

INTERNAL_IPS = ['127.0.0.1', 'localhost']

X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_BROWSER_XSS_FILTER = True

ADMINS = [('Jacob Bom', 'bomjacob@gmail.com')]

WSGI_APPLICATION = 'htxaarhuslan.wsgi.application'

ROOT_URLCONF = 'htxaarhuslan.urls'

# Application definition

INSTALLED_APPS = [
    'rest_framework',
    'rest_framework.authtoken',  # Need this before our main app since we need to overwrite the admin
    'main.apps.MainConfig',
    'dal',
    'dal_select2',
    'jet.dashboard',
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'snowpenguin.django.recaptcha2',
    'sorl.thumbnail',
    'debug_toolbar',
    'ckeditor',
    'ckeditor_uploader',
]

# Middlewares

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Template cnfig

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'main.context_processors.lan',
                'main.context_processors.lp'
            ],
        },
    },
]

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env_var('DB_NAME'),
        'USER': env_var('DB_USER'),
        'PASSWORD': env_var('DB_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization

LANGUAGE_CODE = 'da-dk'

TIME_ZONE = 'Europe/Copenhagen'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = [
    ('da', 'Dansk'),
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = env_var('STATIC_ROOT', None)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# We don't really have a proper login page, so we have to have a needlogin one
LOGIN_URL = '/bruger/needlogin'
LOGIN_REDIRECT_URL = '/'

# Mail stuff
DEFAULT_FROM_EMAIL = 'HTXAarhusLAN <crew@htxaarhuslan.dk>'
SERVER_MAIL = 'server@htxaarhuslan.dk'
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # We use sendgrid to send mail
    SENDGRID_API_KEY = env_var('SENDGRID_API_KEY', None)
    if SENDGRID_API_KEY:
        EMAIL_BACKEND = "sgbackend.SendGridBackend"

# Recaptcha
RECAPTCHA_PRIVATE_KEY = env_var('RECAPTCHA_PRIVATE_KEY')
RECAPTCHA_PUBLIC_KEY = env_var('RECAPTCHA_PUBLIC_KEY')

# JET admin
JET_SIDE_MENU_COMPACT = True
# Just show all themes.
JET_THEMES = [
    {
        'theme': 'default',
        'color': '#47bac1',
        'title': 'Default'
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#555',
        'title': 'Light Gray'
    }
]
JET_SIDE_MENU_ITEMS = [
    {'label': 'Godkendelse og autorisation', 'items': [
        {'name': 'auth.user'},
        {'name': 'auth.group'},
        {'name': 'authtoken.token'}
    ]},
    {'label': 'Generalt', 'items': [
        {'name': 'main.lan'},
        {'name': 'main.event'},
        {'name': 'main.lanprofile'},
        {'name': 'main.foodorder'}
    ]},
    {'label': 'Turnering', 'items': [
        {'name': 'main.tournament'},
        {'name': 'main.game'},
        {'name': 'main.tournamentteam'},
        {'name': 'main.namedprofile'}
    ]}
]

# Challonge credentials
CHALLONGE_USER = env_var('CHALLONGE_USER')
CHALLONGE_API_KEY = env_var('CHALLONGE_API_KEY')

# Rest API framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

# CK editor
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moonocolor',
        # 'uiColor': '#d33e20',
        'toolbar': 'Custom',
        'toolbar_Custom': [
            {'name': 'document', 'items': ['Source']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Table', 'HorizontalRule', 'SpecialChar', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Format', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize']},
            {'name': 'about', 'items': ['About']},
        ],
        'extraPlugins': ','.join([
            'autogrow',
            #  'devtools',
            'autolink',
            'embed',
            'about',
            'lineutils',
            'magicline',
            'table',
            'tabletools'
        ])
    }
}

GOOGLE_FIREBASE_AUTH_KEY = env_var('GOOGLE_FIREBASE_AUTH_KEY')

RESTRICTED_USER_GROUP = env_var('RESTRICTED_USER_GROUP')
