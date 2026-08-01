from .settings import *

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['your-render-domain.com'])
