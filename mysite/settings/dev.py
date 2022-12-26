from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4w$$of)udb)qv8=vs^5vy#8%9+kk73x0u$de0dxg2xl+@s^v1g'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware']

# INSTALLED_APPS = INSTALLED_APPS + ["debug_toolbar",]

INTERNAL_IPS = [
    "localhost",
    "127.0.0.1",
]

try:
    from .local import *
except ImportError:
    pass


AWS_SECRET_ACCESS_KEY = '2TsSrqbnH8+5fYE9w8OAe8r1efcIAYRmpYVWYFWQ2Sk'
AWS_STORAGE_BUCKET_NAME = 'buildly-dev'
AWS_ACCESS_KEY_ID = 'DO00KA2CW3QNV69KAVR4'
AWS_S3_CUSTOM_DOMAIN = 'cms-static.nyc3.digitaloceanspaces.com' + "/" + AWS_STORAGE_BUCKET_NAME
AWS_S3_ENDPOINT_URL  = 'https://cms-static.nyc3.digitaloceanspaces.com'

MEDIA_URL = AWS_S3_CUSTOM_DOMAIN + "/" + AWS_STORAGE_BUCKET_NAME + "/"
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
