from .dev import *

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='mess_manager'),
        'USER': config('POSTGRES_USER', default='mess_admin'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='choose-a-local-password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
