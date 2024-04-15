from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+!6ei8lf-vn^i(u-6*w*)evzpb6w%pz@n#w285o4p=y55vwp)#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

LOGIN_URL = '/login'

# Application definition

INSTALLED_APPS = [
 #   'account.apps.AccountConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'main',
    'account',
    'goal',
    'ckeditor',
    'rest_framework',
    'board',
    'bot',
    'django.contrib.humanize',
    'orders',
    'paycom',
    "django_celery_beat",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
REST_FRAMEWORK = {
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M",
}
AUTH_USER_MODEL = 'account.Account'
ROOT_URLCONF = 'crm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'crm.wsgi.application'

# PAYCOM_API_LOGIN = "Paycom"
# PAYCOM_API_KEY = '5XtVRY%HSkCsMVta0a521fVUrJwBwY6Sq3uE'
# PAYCOM_API_KEY = '5Aye@wSR8JUazhS1MVez?J7ctCBHcIYXGF2O'
# PAYCOM_MERCHANT_ID = '60ae15c4a44459bf07890f7f'
PAYCOM_IS_TEST = False
PAYCOM_API_LOGIN = "Paycom"
# PAYCOM_API_KEY = 'Rzr&GwFdCAu6%1z4hu0CnqWE%P&7BDXyd9pH'
PAYCOM_API_KEY = '5Aye@wSR8JUazhS1MVez?J7ctCBHcIYXGF2O'
PAYCOM_MERCHANT_ID = '60a7a37e7852bd0ebce20d07'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'elektr_crm',
#        'USER': 'elektr',
#        'PASSWORD': 'elektr',
#        'HOST': 'localhost',
#        'PORT': '',
#    }
#}




DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'crm',
        'USER': 'crmuser',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}






#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': 'crmdb',
#        'USER': 'nuriddin',
#        'PASSWORD': '1234567q'
#    }
#}



CRONJOBS = [
    # ('*/10 * * * *', 'account.views.check_company_invoice'),
    ('0 */6 * * *', 'account.views.birthday_sms_send') #6 soatda bir sms jo'natadi tug'ilgan kunlarga
]

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'uz'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']

LANGUAGES = [
    ['uz', "O'zbek"],
    ['en', "English"],
    ['ru', "Russian"],
]
LANGUAGE = 'uz'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR/'static']
# STATIC_ROOT = BASE_DIR / 'static'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR/'media'

CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"
CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/0"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TIMEZONE = "Asia/Tashkent"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_WORKER_HOSTNAME = '127.0.0.1'
CELERY_IMPORTS = ("main.tasks")


