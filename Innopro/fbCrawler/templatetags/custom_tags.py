from django import template
from fbCrawler.models import *

from sqlalchemy import create_engine
import pymysql

connect_info = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(
    'admin', 'password', 'rds-mysql.ctugs84fp5hq.ap-southeast-1.rds.amazonaws.com', 3306, 'Innopro')  # 1
engine = create_engine(connect_info)

register = template.Library()


@register.filter(name='get_fb_name')
def getFbName(fbuid):
    name = Members.objects.get(fbid=fbuid).name
    return name


@register.filter(name='get_fb_url')
def getFbUrl(fbuid):
    url = Members.objects.get(fbid=fbuid).user_profile_url
    return url


@register.filter(name='get_fee_list')
def getFeeList(fbuid, feeList):
    res = list(filter(lambda l: l['fbuid'] == fbuid, feeList))
    try:
        data = res[0]['折扣後自取價']
    except Exception as e:
        print(e)
        data = 0

    # url = Members.objects.get(fbid=fbuid).user_profile_url
    return data


@register.filter(name='get_helper')
def getHelper(fbuid):
    # helper = Members.objects.get(fbid=fbuid).helper
    # print(helper)
    print(result)
    return result
