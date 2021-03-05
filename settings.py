# coding=utf-8
import os
import sys

DOMAIN = 'www.coolvox.com'

COOKIE_SECRET = "R8sEDELfR3yy0M2dfvOgEEIUUZ=Vxbhw3TSWZCzwQeGxff"
COOKIE_DOMAIN = "coolvox.com"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

DB_URL = None
REDIS_SETTINGS = None
DEBUG = False

SEARCH_API_HOST = 'http://localhost:8081/coolvox_search/'
PAY_API_HOST = 'http://60.190.28.43:8160/'

ENV = None

access_key_id = ''
access_key_secret = ''
endpoint = ''
bucket_name = ''
AMQP_URL = "amqp://test:test@192.168.0.13:5672/test"


PDF_BUCKET = {
    'endpoint': 'http://oss-cn-shanghai.aliyuncs.com',
    'bucket': 'kanjian-star-sh'
}

ALI_MESSAGE = {
    'ali_accesskey': '',
    'ali_access_key_secret': ''
}


def apply_env(env):

    global DB_URL
    global ENV
    global REDIS_SETTINGS
    global SEARCH_API_HOST
    global PAY_API_HOST
    global DEBUG
    global COOKIE_DOMAIN
    global DOMAIN
    global STATIC_DIR
    global AMQP_URL
    ENV = env
    if env == 'personal':
        DB_URL = 'mysql+pymysql://root:@localhost/trade_backend?charset=utf8&use_unicode=1'
        COOKIE_DOMAIN = 'kanjian.com'
        DOMAIN = 'kanjian.com'
        REDIS_SETTINGS = {
            'PORT': 15010,
            'DB': 0,
        }
    elif env == 'dev':
        DB_URL = 'mysql+pymysql://root:root@192.168.0.13/trade_backend?charset=utf8&use_unicode=1'
        SEARCH_API_HOST = 'http://192.168.0.13:8050/'
        PAY_API_HOST = 'http://192.168.0.106:15035/'
        COOKIE_DOMAIN = ''
        DOMAIN = 'kanjian.com'
        DEBUG = False
        REDIS_SETTINGS = {
            'PORT': 15010,
            'DB': 0,
        }
        STATIC_DIR = os.path.join(os.path.split(BASE_DIR)[0], 'static')
        AMQP_URL = "amqp://test:test@192.168.0.13:5672/test"
    elif env == 'test':
        DB_URL = 'mysql+pymysql://root:root@192.168.0.13/coolvox-test?charset=utf8&use_unicode=1'
        # SEARCH_API_HOST = 'http://coolvox-search.kanjiancs.com:15025/'
        # PAY_API_HOST = 'http://coolvox-pay.kanjiancs.com:15035/'
        COOKIE_DOMAIN = ''
        DOMAIN = 'kanjian.com'
        REDIS_SETTINGS = {
          'HOST': 'redis.star-test.svc.cluster.local',
          'PORT': 15010,
          'DB': 0,
        }
        AMQP_URL = "amqp://coolvox:D8RARZYRKGnv3b9g@rabbitmq.star-test.svc.cluster.local:5672"
    elif env == 'production':
        DB_URL = 'mysql+pymysql://coolvox:A9FTcKKR@192.168.100.50/coolvox?charset=utf8&use_unicode=1'
        SEARCH_API_HOST = 'http://coolvox-search.kanjiancs.com:15025/'
        PAY_API_HOST = 'http://coolvox-pay.kanjiancs.com:15035/'
        REDIS_SETTINGS = {
            'HOST': '192.168.100.16',
            'PORT': 15050,
            'DB': 9,
        }
    elif env == 'aliyun-production':
        DB_URL = 'mysql+pymysql://coolvox:A9FTcKKR@rm-uf6a5i36faa957251.mysql.rds.aliyuncs.com/coolvox?charset=utf8&use_unicode=1'
        SEARCH_API_HOST = 'http://coolvox-search-api.star-sh.svc.cluster.local:15025/'
        PAY_API_HOST = 'http://coolvox-pay.star-sh.svc.cluster.local:15035/'
        REDIS_SETTINGS = {
            'HOST': 'r-uf65236174539204.redis.rds.aliyuncs.com',
            'PORT': 6379,
            'DB': 9,
            'PASSWORD': 'nXccPPxx8n2Zfu4MVxR91'
        }
        AMQP_URL = "amqp://coolvox:D8RARZYRKGnv3b9g@rabbitmq.star-sh.svc.cluster.local:5672"
    else:
        raise NotImplementedError


def parse_cmd():
    from tornado.options import options, define, parse_command_line
    define(name="config", default="dev")
    define(name="port", default="10037")

    args = sys.argv
    new_args = [args[0]]
    for i in range(1, len(args)):
        if not args[i].startswith("-") or args[i] == "--":  # ignore arguments not startswith '-'
            break
        arg = args[i].lstrip("-")
        key, equals, value = arg.partition("=")
        key = key.replace('_', '-')
        if key in options._options:
            new_args.append(args[i])

    parse_command_line(args=new_args)

    apply_env(options.config)


parse_cmd()
