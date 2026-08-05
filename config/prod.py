from .settings import *

DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['mess-manager-7pu0.onrender.com'])
