from fbCrawler.models import (Product, Members, Orders, Helper)
import pandas as pd
import os
import json
import datetime

from django.utils import timezone
from django.conf import settings
from django.utils.timezone import make_aware
from django.db.models import Q

from sqlalchemy import create_engine
import pymysql


connect_info = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(
    settings.CONFIG_DATA.get('DBACCOUNT'), settings.CONFIG_DATA.get('DBPASSWORD'),
    settings.CONFIG_DATA.get('DBHOST'), settings.CONFIG_DATA.get('DBPORT'), settings.CONFIG_DATA.get('DBNAME'))
engine = create_engine(connect_info)


def getFeeListAll(sessionId):
    df = pd.read_sql('''select *,  fbCrawler_members.name as user_name,
					fbCrawler_members.user_profile_url as member_fb_url,
                    fbCrawler_helper.name as helper_name, fbCrawler_helper.user_profile_url as helper_url
                    from feeList
                    inner join fbCrawler_members 
                    on feeList.fbuid = fbCrawler_members.fbid
                    inner join fbCrawler_helper
                    on fbCrawler_members.helper_id = fbCrawler_helper.id
                    where session={};'''.format(sessionId), con=engine)
    return df


def getHelperList():
    df = pd.read_sql('''select fbCrawler_helper.name, fbCrawler_members.fbid from fbCrawler_helper 
        INNER JOIN fbCrawler_members ON fbCrawler_members.helper_id = fbCrawler_helper.id;''', con=engine)
    return df


def updateFeeList(ship_method, transfer_amount, transfer_account, notes, deliver_time, deliver_date, fbuid, sessionId):
    isSuccess = False
    try:
        sql = '''UPDATE feeList SET ship = '{}', 
            transfer_amount = '{}', transfer_account = '{}', 
            notes = '{}', deliver_time = '{}', deliver_date = '{}'
            WHERE fbuid = {} and session = {}'''.format(
            ship_method, transfer_amount, transfer_account, notes, deliver_time, deliver_date, fbuid, sessionId)
        result = engine.execute(sql)
        isSuccess = True
    except Exception as e:
        print(e)
    return isSuccess


def feeListInfo(fbuid, sessionId):
    sql = '''select ship, transfer_amount, transfer_account, 
            notes, deliver_time, deliver_date from feeList WHERE fbuid = {} and session = {}'''.format(fbuid, sessionId)
    result = engine.execute(sql).fetchone()
    data = {
        'ship': result[0] if result[0] != None else 'ship',
        'transfer_amount': result[1] if result[1] != 0 else None,
        'transfer_account': None if (result[2] == '0' or result[2] == None) else result[2],
        'notes': None if result[3] == 'None' else result[3],
        'deliver_time': 'all' if result[4] == None else result[4],
        'deliver_date': None if result[5] == 'None' else result[5]
    }
    return data


def afterSettleList(session, fbuid=None, method='append'):
    #     check_exist=pd.read_sql('select * from afterSettleList where session='+str(session),con=engine)#防止重複結算
    #     check_exist['session']=check_exist['session'].astype(str)
    #     if session not in check_exist['session'].values:

    if(fbuid):
        df = pd.read_sql(
            'select * from confirmPurchaseRight where fbuid = {} and session= {} ;'.format(str(fbuid), str(session)), con=engine, index_col=['session', 'fbuid'])
    else:
        df = pd.read_sql(
            'select * from confirmPurchaseRight where session= {} ;'.format(str(session)), con=engine, index_col=['session', 'fbuid'])

    dfx = df.loc[:, ['username', 'getSure', 'wineID', 'wineName', 'limit', 'orginalOrderCount', 'orderCount', 'giftBottle', 'orderCountAfterSale',
                     'price', 'totalPrice']]
    dfx['limit'] = dfx['limit'].apply(
        lambda s: "限加"+str(s) if s > 0 else '無限加限制')
    df_sorry = dfx[dfx['getSure'] == 'sorry']
    df_sorry['orderCountAfterSale'] = 0
    df_sorry['totalPrice'] = 0

    df_get = dfx[dfx['getSure'] == 'get']

    final_list = pd.concat([df_get, df_sorry])
    final_list = final_list.rename(columns={'username': 'FB姓名', 'getSure': '購買權確認', 'wineID': '商品編號', 'wineName': '商品名稱',
                                            'limit': '購買限制', 'orginalOrderCount': '留言購買數', 'orderCount': '結算確認購買數量', 'giftBottle': '優惠贈送量',
                                            'orderCountAfterSale': '扣除贈送量後計價數', 'price': '商品單價', 'totalPrice': '商品總價'})
    final_list['備註'] = ['未排到' if (a == 'sorry')
                        else b if (a == 'get') & (b != '無限加限制') & (c > 0)
                        else '留言購買數大於庫存數,修正為最大可買數。' if (a == 'get') & (b == '無限加限制') & (c > d)
                        else '已確認'
                        for a, b, c, d in zip(final_list['購買權確認'], final_list['購買限制'], final_list['留言購買數'], final_list['結算確認購買數量'])]
    final_list = final_list.reset_index()
    # final_list.to_sql(name='afterSettleList', con=engine, if_exists=method)
#     else:
#         print('afterSettleList session is duplicated')
    return final_list.sort_index()


def feeList(session, fbuid=None, method='append'):
    #     check_exist=pd.read_sql('select * from feeList where session='+str(session),con=engine)#防止重複結算
    #     check_exist['session']=check_exist['session'].astype(str)
    #     if session not in check_exist['session'].values:
    if(fbuid):
        df = pd.read_sql(
            'select * from calDiliverCostFinal where fbuid = {} and session={} ;'.format(
                str(fbuid), str(session)), con=engine, index_col=['session', 'fbuid'])
    else:
        df = pd.read_sql(
            'select * from calDiliverCostFinal where session={} ;'.format(
                str(session)), con=engine, index_col=['session', 'fbuid'])

    # 製作訂單編號
    df['index'] = (df['index']+1).apply(lambda s: '000'+str(s) if s <
                                        10 else '00'+str(s) if s < 100 else '0'+str(s) if s < 1000 else str(s))
    df['訂單編號'] = str(session)+df['index']
    df = df.loc[:, ['訂單編號', 'orderCount', 'deilverFreeAll', 'deilverFreeAllbottle', 'discountAll', 'selfGetCost', 'diliverCostAfterDiscountAll',
                    'diliverCostAfterDeilverFreeAll', 'totalPriceIncludeDC']]

    df['deilverFreeAll'] = df['deilverFreeAll'].apply(
        lambda s: "滿"+str(s)+'元免運' if s > 0 else '無')
    df['deilverFreeAllbottle'] = df['deilverFreeAllbottle'].apply(
        lambda s: "滿"+str(s)+'件免運' if s > 0 else '無')
    df['discountAll'] = df['discountAll'].apply(
        lambda s: "全團"+str(s*10)+'折優惠' if s != 1 else '無全團折扣優惠')

    df = df.rename(columns={'orderCount': '結算確認購買數量', 'deilverFreeAll': '金額達標免運優惠', 'deilverFreeAllbottle': '瓶數達標免運優惠',
                            'discountAll': '全團折扣優惠', 'selfGetCost': '折扣前價格', 'diliverCostAfterDiscountAll': '折扣後自取價',
                            'diliverCostAfterDeilverFreeAll': '運費', 'totalPriceIncludeDC': '含運費總價'})
    df = df.reset_index()
    # df.to_sql(name='feeList', con=engine, if_exists=method)
#     else:
#         print('feeList session is duplicated')
    return df.sort_index()
