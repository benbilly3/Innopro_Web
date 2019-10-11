from .base import *

DEBUG = False

if 'facebook_account' in os.environ:
    CONFIG_DATA = {
        "facebook_account": os.environ.get('facebook_account'),
        "facebook_password": os.environ.get('facebook_password'),
        "DBACCOUNT": os.environ.get('DBACCOUNT'),
        "DBPASSWORD": os.environ.get('DBPASSWORD'),
        "DBHOST": os.environ.get('DBHOST'),
        "DBPORT": os.environ.get('DBPORT'),
        "DBNAME": os.environ.get('DBNAME')
    }
else:
    with open(os.path.join(BASE_DIR, "config.json"), 'r', encoding='utf8') as file:
        CONFIG_DATA = json.load(file)

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': CONFIG_DATA['DBNAME'],
        'USER': CONFIG_DATA['DBACCOUNT'],
        'PASSWORD': CONFIG_DATA['DBPASSWORD'],
        'HOST': CONFIG_DATA['DBHOST'],
        'PORT': CONFIG_DATA['DBPORT'],
        'OPTIONS': {
            # "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            # 插入 emoji 的時候會報錯：1366, "Incorrect string value: '\\xF0\\x9F\\x8F\\x85</...' for column 'html' at row 1"
            # Warning: (1366, "Incorrect string value: '\\xF0\\x9F\\xA5\\x87</...' for column 'html' at row 1")
            # 所以將預設的charset 改成 mb4 （字元數較長的格式，可以放入emoji）
            # https://stackoverflow.com/questions/44496101/how-to-insert-emoji-into-mysql-5-5-and-higher-using-django-orm
            'charset': 'utf8mb4',
            'use_unicode': True,                                                            
        }
    }
}