# Create your views here.
import io
import csv
import codecs
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views import View
from django.views.generic import FormView

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import auth, messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Product, Members, Orders, Session, Checkout, Helper, Group, BankStatement, settlementRule
from .forms import BankStatementForm
from django.db.models import Sum
from django.urls import reverse_lazy
from .utils import *

import pandas as pd
import datetime
from pytz import timezone
import json


"""
----- 會員登入、權限管理 -----
"""

"""
登入
"""


@method_decorator(csrf_exempt, name='dispatch')
class MemberLoginView(View):
    def get(self, request):
        context = {
            'message': "login"
        }
        if request.user.is_authenticated:
            return redirect('sessioIndex')

        return render(request, 'login.html', context=context)

    def post(self, request):
        print(self.request.POST)
        postData = self.request.POST.dict()
        print(postData)

        result = {
            'status': True,
            'isUser': False,
            'resMessage': None
        }

        appuid = postData['id']
        print(appuid)
        # fb 登入之後回傳用戶登入狀態
        if 'fburl' not in postData:
            # check if linked
            try:
                member = Members.objects.get(fb_login_app_id=appuid)
                user = member.user
                if(member.user):
                    auth.login(request, member.user)
                    result['isUser'] = True
                else:
                    print('has appuid not create users yet')

            except Members.DoesNotExist:
                print('not existed, have to create new user and link appuid')

            except Exception as e:
                print(e)

            return JsonResponse(result)
        # 用戶回傳 fb_url 連結帳戶與創建 user
        else:
            fburl = postData['fburl']
            print('with url')
            member = self.urlToMember(fburl)
            if(member):
                user = member.user
                print('is member')
                if(user):
                    result['resMessage'] = '此 fb 連結已經被註冊過，請確認有無其他 fb 帳號，或是聯繫小幫手'
                else:
                    print(member)
                    newUser = User(username=member.fbid)
                    newUser.save()
                    member.fb_login_app_id = appuid
                    member.user = newUser
                    member.save()
                    auth.login(request, newUser)
                    # result['resMessage'] = '創建用戶完成，轉跳至團購頁面'
            else:
                result['resMessage'] = '此 fb 連結沒有參與團購記錄，或是請再次確認 fb 連結符合下方形式'

            # 確認 fburl 是否已經連結
            return JsonResponse(result)

    def urlToMember(self, fburl):
        fburl = fburl.replace('m.facebook.com', 'facebook.com')
        print('Searching {}\'s member record'.format(fburl))
        member_qs = Members.objects.extra(
            where=["%s LIKE CONCAT('%%',user_profile_url,'%%')"], params=[fburl])
        member = member_qs.get() if len(member_qs) != 0 else None
        return member


"""
登出
"""


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login/')


"""
fbUrl 轉換 fbUid
"""


@csrf_exempt
def fbUrlToId(request):
    postData = request.POST.dict()
    fburl = postData['fb_url']
    fburl = fburl.replace('m.facebook.com', 'facebook.com')
    print('Searching{}\'s orders'.format(fburl))
    member_qs = Members.objects.extra(
        where=["%s LIKE CONCAT('%%',user_profile_url,'%%')"], params=[fburl])

    fbuid = member_qs.get().fbid if len(member_qs) != 0 else None
    isMember = True if fbuid else False

    resp = {'fbuid': fbuid, 'isMember': isMember}
    print('search result: {}'.format(member_qs))
    return HttpResponse(json.dumps(resp), content_type="application/json")


"""
預設首頁 -> sessionIndex
"""


def index(request):
    return redirect('sessioIndex')


"""
----- 用戶前台 -----
"""

"""
團次列表
"""


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class SessionView(View):
    def get(self, request, session_id=None):
        user = request.user
        member = Members.objects.get(user=user)

        context = {
            'message': None,
            'status': None,
            'session': None,
            'allSessions': None,
            'user': user,
            'member': member
        }

        # 如果 url 沒有參數：列出用戶參與的所有 session
        if(not session_id):
            orders = Orders.objects.filter(member=member)
            unique_session_list = list(
                orders.values_list('session', flat=True))
            sessions = Session.objects.filter(id__in=unique_session_list)
            context['allSessions'] = sessions
            return render(request, 'session/allSessions.html', context=context)

        try:
            session = Session.objects.get(session_id=session_id)
            session_status = session.status
            context['status'] = session_status
            context['session'] = session
        except Session.DoesNotExist:
            print('session does not exit')
            context['message'] = '查無本團次，請重新搜尋'
            return render(request, 'session/annoucement.html', context=context)
        except Exception as e:
            print('error')
            print(e)

        if(session_status == 'open' or session_status == 'system_updating' or session_status == 'cloced'):
            print('open/ systemupdate/ closed')
            return render(request, 'session/annoucement.html', context=context)
        elif(session_status == 'update_orders'):
            print('update_orders')
            return render(request, 'session/updateOrder.html', context=context)
        elif(session_status == 'checkout'):
            print('checkout')
            return render(request, 'session/confirmedOrder.html', context=context)
        else:
            print('else')
            print(session_status)

        return render(request, 'session/annoucement.html', context=context)

    def post(self, request, session_id):
        if self.request.method == "POST" and self.request.is_ajax():
            print('yoo')
            print(self.request.POST)
            result = {'status': True}
            return JsonResponse(result)


"""
結算前更新訂單（購物車）
"""


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class sessionUpdateOrderView(View):
    def get(self, request, session_id=None):
        context = {
            'message': None,
            'sessionExist': False,
            'hasOrder': False,
            'orders': None,
            'session': None,
            'member': None,
            'total_price': 0
        }
        # Session id 不存在
        session_qs = Session.objects.filter(session_id=session_id)

        if session_qs.count() == 0:
            context['message'] = '團次錯誤，請到團次列表查詢參與團次'
            return render(request, 'session/updateOrder.html', context=context)

        session = session_qs[0]
        if session.status != 'update_orders':
            context['message'] = '本團次目前沒有開放修正數量，有疑問請洽小幫手'
            return render(request, 'session/updateOrder.html', context=context)
        else:
            context['sessionExist'] = True

        session = session_qs[0]
        member = Members.objects.get(user=request.user)
        # 查詢此用戶在此 session 有無訂單
        orders_qs = Orders.objects.filter(member=member, session=session)
        if orders_qs.count() < 1:
            context['message'] = '您並無本團次訂單，有疑問請洽小幫手'
            return render(request, 'session/updateOrder.html', context=context)
        else:
            orders_qs = Orders.objects.filter(member=member, session=session)

            # list(ods.values()),objects轉pandas
            df_ods = pd.DataFrame(
                list(orders_qs.values('member_id', 'member__name',
                                      'product__wine_id', 'product__name', 'product__product_article_link', 'amount',
                                      'product__price', 'product__erp_no')
                     )
            )

            orders_qs2 = Orders.objects.filter(session=session)
            df_ods2 = pd.DataFrame(list(orders_qs2.values(
                'member_id', 'product__wine_id', 'amount')))
            df_ods2 = df_ods2.set_index('product__wine_id')
            df_ods2['total_amount'] = df_ods2.groupby(
                'product__wine_id')['amount'].sum()

            df_ods = df_ods.set_index('product__wine_id')
            sr = settlementRule.objects.filter(session=session)
            df_sr = pd.DataFrame(list(sr.values(
                'wineID', 'stockNum', 'stockNumFalse', 'limit', 'sale', 'deliverFree')))
            df_sr = df_sr.set_index('wineID')
            for i in ['stockNum', 'stockNumFalse', 'limit', 'sale', 'deliverFree']:
                df_ods[i] = df_sr[i]
            total_amount = df_ods2['total_amount']
            total_amount = total_amount[~total_amount.duplicated()]
            df_ods['total_amount'] = total_amount
            df_ods['amount'] = df_ods['amount'].astype(int)
            df_ods['stockNumFalse'] = df_ods['stockNumFalse'].astype(int)
            df_ods['bgc'] = df_ods['total_amount'] - df_ods['stockNumFalse']
            df_ods['limit'] = df_ods['limit'].apply(
                lambda s: str(s).replace('0', '無'))
            df = df_ods.sort_values('bgc', ascending=True)
            df = df.reset_index()
            orders_qs = df.T.to_dict().values()

            context['orders'] = list(orders_qs)
            total_price = 0
            for order in orders_qs:
                total_price += order['amount'] * order['product__price']
            context['total_price'] = total_price

            context['hasOrder'] = True
            context['orders'] = list(orders_qs)
            context['session'] = session
            context['member'] = member
            # total price
            total_price = 0
            for order in orders_qs:
                total_price += order['amount'] * order['product__price']
            context['total_price'] = total_price

        return render(request, 'session/updateOrder.html', context=context)

    # submit update order
    def post(self, request, session_id=None):
        postData = request.POST.dict()
        new_amount_data = json.loads(postData['new_amount_data'])
        member = Members.objects.get(user=request.user)
        session = Session.objects.get(session_id=session_id)

        resp = {
            'status': 'failed',
        }

        try:
            # 更新用戶基本資料
            new_shipname = postData['new_shipname']
            new_email = postData['new_email']
            if new_shipname:
                member.shipname = new_shipname
            if new_email:
                member.email = new_email
            member.save()

            # 更新訂單
            for item in new_amount_data:
                item_id = item['item_id']
                new_amount = int(item['item_amount'])
                order = Orders.objects.get(
                    member=member, product__wine_id=item_id, session=session)
                if order.amount == new_amount:
                    pass
                else:
                    # if new_amount > order.amount or new_amount < 0:
                    if new_amount < 0:
                        pass
                    else:
                        order.amount = new_amount
                        order.save()

            resp['status'] = 'success'

        except Exception as e:
            print(e)

        return HttpResponse(json.dumps(resp), content_type="application/json")


@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def submitUpdateOrder(request):
    postData = request.POST.dict()

    resp = {
        'status': 'success'
    }
    new_amount_data = json.loads(postData['new_amount_data'])
    try:
        member = Members.objects.get(fbid=postData['user_fb_id'])
        new_shipname = postData['new_shipname']
        new_email = postData['new_email']
        if new_shipname:
            member.shipname = new_shipname
        if new_email:
            member.email = new_email
        member.save()
        for item in new_amount_data:
            item_id = item['item_id']
            new_amount = int(item['item_amount'])
            order = Orders.objects.get(
                member=member, product__wine_id=item_id)
            if order.amount == new_amount:
                pass
            else:
                # if new_amount > order.amount or new_amount < 0:
                if new_amount < 0:
                    pass
                else:
                    order.amount = new_amount
                    order.save()

    except Exception as e:
        print(e)
        resp['status'] = 'failed'

    return HttpResponse(json.dumps(resp), content_type="application/json")


"""
結算後訂單（匯款）
"""


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class sessionConfirmedOrder(View):
    def get(self, request, session_id=None):
        context = {
            'session': None,
            'member': None,
            'message': None,
            'checkout': None,
            'orders': None,
        }

        user = request.user
        member = Members.objects.get(user=user)
        context['member'] = member

        # check if session exist
        session_qs = Session.objects.filter(session_id=session_id)
        if session_qs.count() == 0:
            context['message'] = '團次錯誤，請到團次列表查詢參與團次'
            return render(request, 'session/confirmedOrder.html', context=context)

        session = session_qs[0]
        context['session'] = session

        # check session status
        # if session.status != 'update_orders':
        #     context['message'] = '本團次目前沒有開放修正數量，有疑問請洽小幫手'
        #     return render(request, 'session/updateOrder.html', context=context)
        # else:
        #     context['sessionExist'] = True

        # check if order exist
        orders_qs = Orders.objects.filter(member=member, session=session)
        if orders_qs.count() < 1:
            context['message'] = '您並無本團次訂單，有疑問請洽小幫手'
            return render(request, 'session/confirmedOrder.html', context=context)
        else:
            checkout_qs = Checkout.objects.filter(
                member=member, session=session)
            checkout = checkout_qs[0] if checkout_qs.count() > 0 else None
            context['checkout'] = checkout
            context['orders'] = orders_qs
            context['member'] = member

        return render(request, 'session/confirmedOrder.html', context=context)

    def post(self, request, session_id=None):
        postData = request.POST.dict()
        print(postData)
        resp = {
            'status': 'failed'
        }

        try:
            user = request.user
            member = Members.objects.get(user=user)
            session = Session.objects.get(session_id=session_id)
            checkout = Checkout.objects.get(member=member, session=session)

            # member data
            memberData = {
                'email': postData['email'],
                'phone': postData['phone'],
                'zipcode': postData['zipcode'],
                'city': postData['city'],
                'county': postData['county'],
                'address': postData['address'],
                'shipname': postData['name'],
                'invoice_id': postData['invoice_id'],
                'invoice_title': postData['invoice_title']
            }

            for key, value in memberData.items():
                setattr(member, key, value)
            member.save()

            # checkout data
            checkoutData = {
                'ship_time': postData['ship_time'],
                'ship_date': postData['ship_date'],
                'ship_method': postData['ship_method'],
                'transfer_amount': postData['transfer_amount'],
                'transfer_account': postData['transfer_account'],
                'notes': postData['notes'],
            }

            for key, value in checkoutData.items():
                setattr(checkout, key, value)
            checkout.save()

            resp['status'] = 'success'
        except Exception as e:
            print(f'error when submitting transfer date, member: {member}')
            print(e)

        return HttpResponse(json.dumps(resp), content_type="application/json")


@csrf_exempt
def submitTransferInfo(request):
    postData = request.POST.dict()
    print(postData)
    resp = {
        'status': 'success'
    }
    # try:
    fbuid = postData['user_fb_id']
    member = Members.objects.get(fbid=fbuid)

    # Member
    memberData = {
        'email': postData['email'],
        'phone': postData['phone'],
        'zipcode': postData['zipcode'],
        'city': postData['city'],
        'county': postData['county'],
        'address': postData['address'],
        'shipname': postData['name'],
        'invoice_id': postData['invoice_id'],
        'invoice_title': postData['invoice_title']
    }

    for key, value in memberData.items():
        setattr(member, key, value)
    member.save()

    # FeeList
    ship_method = postData['ship_method'] if postData['ship_method'] != '' else None
    transfer_amount = postData['transfer_amount'] if postData['transfer_amount'] != '' else 0
    transfer_account = postData['transfer_account'] if postData['transfer_account'] != '' else 0
    notes = postData['notes'] if postData['notes'] != '' else None
    deliver_time = postData['deliver_time'] if postData['deliver_time'] != '' else None
    deliver_date = postData['deliver_date'] if postData['deliver_date'] != '' else None
    sessionId = '20190812'

    isSqlSuccess = updateFeeList(
        ship_method, transfer_amount, transfer_account, notes, deliver_time, deliver_date, fbuid, sessionId)
    print('Sql exec', isSqlSuccess)

    # except Exception as e:
    #     print(e)
    #     resp['status'] = 'failed'

    return HttpResponse(json.dumps(resp), content_type="application/json")


def updateOrder(request, fbuid=None):
    if(not fbuid):
        context = {
            'input': False,
            'fbuid': None
        }
    else:
        context = {
            'input': True,
            'fbuid': fbuid
        }
        print('fbuid is {}'.format(fbuid))
        member_qs = Members.objects.filter(fbid=fbuid)
        if len(member_qs) != 0:
            member = member_qs.get()
            monthly_orders = Orders.objects.filter(
                member=member, product__month__in=['08'])

        if(len(member_qs) == 0 or len(monthly_orders) == 0):
            context['results'] = None
        else:
            context['results'] = True
            context['member'] = member
            context['orders'] = monthly_orders
            all_price = 0
            for order in monthly_orders:
                item_price = order.product.price
                order_count = order.amount
                item_all = item_price * order_count
                all_price += item_all
            context['all_price'] = all_price

    return render(request, 'updateOrder.html', context=context)


def confirmedOrder(request, fbuid=None):
    if(not fbuid):
        context = {
            'input': False,
            'fbuid': None
        }
    else:
        context = {
            'input': True,
            'fbuid': fbuid,
            'orders': None
        }
        # try:
        context['member'] = Members.objects.get(fbid=fbuid)
        sessionId = '20190812'
        df_after_settle = afterSettleList(sessionId, fbuid)
        user_orders = df_after_settle[df_after_settle['fbuid'] == int(
            fbuid)]
        list_after_settle = list(user_orders.T.to_dict().values())

        df_feelist = feeList(sessionId, fbuid)
        user_feelist = df_feelist[df_feelist['fbuid'] == int(fbuid)]
        list_feelist = list(user_feelist.T.to_dict().values())

        context['orders'] = list_after_settle
        context['final'] = list_feelist[0]

        feeInfo = feeListInfo(fbuid, sessionId)
        context['feeListInfo'] = feeInfo

        # except Exception as e:
        #     print(e)
        #     context['orders'] = None

    return render(request, 'confirmedOrder.html', context=context)


"""
----- 小幫手管理介面 -----
"""

"""
所有用戶頁面
"""


@user_passes_test(lambda u: u.is_superuser)
def members(request, year='', month='', fbuid=''):
    if(not year or not month):
        year = datetime.datetime.today().year
        month = datetime.datetime.today().month

    if(not fbuid):
        # All users
        members = Members.objects.all()
        orders = None
        if(year and month):
            members = Members.objects.filter(orders__product__month__in=[
                month], orders__product__year__in=[year]).distinct().order_by('id')
    else:
        # only one user and print all orders
        members = Members.objects.filter(fbid=fbuid)
        orders = Orders.objects.filter(member=members[0])

    context = {
        'year': year,
        'month': month,
        'members': members,
        'orders': orders
    }
    return render(request, 'members.html', context=context)


"""
全品項
"""


@user_passes_test(lambda u: u.is_superuser)
def items(request, year='', month=''):
    if(not year or not month):
        year = datetime.datetime.today().year
        month = datetime.datetime.today().month

    products = Product.objects.filter(
        available=True,
        year=year,
        month=month
    ).order_by('wine_id')
    context = {
        'year': year,
        'month': month,
        'items': products
    }
    return render(request, 'items.html', context=context)


"""
各期銷售記錄
"""


@user_passes_test(lambda u: u.is_superuser)
def sales(request, session_id=None):

    context = {
        'allSessions': None,
        'reportType': '銷售列表',
        'reportUrl': 'sales',
        'session': None,
        'products': None,
        'total_income': None
    }

    if not session_id:
        allSessions = Session.objects.all().order_by('-year', '-month')
        context['allSessions'] = allSessions

        return render(request, 'reports/sales.html', context=context)
    else:
        currentSession = Session.objects.get(session_id=session_id)
        sessionProducts = Product.objects.filter(session=currentSession)
        productList = list(sessionProducts)

        total_income = 0
        for product in productList:
            productTotalOrders = Orders.objects.filter(
                product=product).aggregate(Sum('amount'))['amount__sum']
            product.totalOrders = productTotalOrders

            productIncome = productTotalOrders*product.price
            product.income = productIncome
            total_income += productIncome

        context['session'] = currentSession
        context['products'] = productList
        context['total_income'] = total_income

        return render(request, 'reports/sales.html', context=context)


"""
結算後大表單
"""


@user_passes_test(lambda u: u.is_superuser)
def bigtable(request, session_id=None):
    context = {
        'allSessions': None,
        'reportType': '結算後大表單',
        'reportUrl': 'bigtable',
        'session': None,
        'datas': None
    }

    if not session_id:
        allSessions = Session.objects.all().order_by('-year', '-month')
        context['allSessions'] = allSessions
        return render(request, 'reports/bigtable.html', context=context)
    else:
        session = Session.objects.get(session_id=session_id)
        ods = Orders.objects.filter(
            session=session).filter(~Q(amount=0)).filter(~Q(minus_free_amount=0))
        df_ods = pd.DataFrame(
            list(
                ods.values(
                    'member_id', 'member__name', 'member__helper__name',
                    'product__wine_id', 'product__name', 'amount', 'minus_free_amount',
                    'product__price', 'notes', 'product__erp_no'
                )
            )
        )

        df_ods['order_total_price'] = df_ods['minus_free_amount'] * \
            df_ods['product__price']
        df_ods = df_ods.sort_values(by=['member_id', 'product__wine_id'])
        orders = df_ods.T.to_dict().values()

        cos = Checkout.objects.filter(session=session)
        df_cos = pd.DataFrame(list(cos.values()))
        checkouts = df_cos.T.to_dict().values()

        allUserInfo = []
        mbids = df_ods.member_id.unique()
        for mb in mbids:
            temp = {
                'orders': None,
                'checkout': None
            }

            orders = df_ods[df_ods['member_id'] == mb]
            checkout = df_cos[df_cos['member_id'] == mb]
            temp['orders'] = list(orders.T.to_dict().values())
            temp['checkout'] = list(checkout.T.to_dict().values())
            total_amount = 0
            for order in temp['orders']:
                total_amount += order['minus_free_amount']
            temp['checkout'][0]['total_amount'] = total_amount
            allUserInfo.append(temp)

        context['session'] = session
        context['datas'] = allUserInfo

        return render(request, 'reports/bigtable.html', context=context)


"""
用戶匯款資訊頁面/ 用戶對帳資訊
"""


@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class MemberTransferView(View):
    def get(self, request, session_id=None):
        context = {
            'allSessions': None,
            'reportType': '匯款資訊',
            'reportUrl': 'memberTransfer',
            'session': None,
            'checkouts': None
        }

        if not session_id:
            allSessions = Session.objects.all().order_by('-year', '-month')
            context['allSessions'] = allSessions
            return render(request, 'reports/memberTransfer.html', context=context)
        else:
            # 計算實際應支付價錢
            def calAP(cos):
                if (cos['ship_method'] == 'ship'):
                    return cos['total_price']
                else:
                    return cos['price_after_disc']

            # 設定不同狀態匯款資訊的背景顏色
            def transferStatus(d):
                related_ts = df_tss[(df_tss['last_five'] == d['transfer_account']) & (
                    df_tss['deposit_amount'] == d['transfer_amount'])]
                if related_ts.empty:
                    return 'white'
                else:
                    return 'lemonchiffon'

            session = Session.objects.get(session_id=session_id)
            cos = Checkout.objects.filter(session=session)
            df_cos = pd.DataFrame(
                list(
                    cos.values(
                        'member_id', 'member__name', 'member__fbid', 'member__helper__name',
                        'member__email', 'member__phone', 'member__shipname', 'member__user_profile_url',
                        'member__address', 'member__city', 'member__county', 'member__zipcode',
                        'member__invoice_id', 'member__invoice_title',
                        'checkout_id', 'ship_method', 'ship_time', 'ship_date',
                        'price_before_disc', 'price_after_disc',
                        'ship_fee', 'total_price', 'transfer_amount', 'transfer_account', 'notes', 'helper_notes'
                    )
                )
            )
            tss = BankStatement.objects.all()
            df_tss = pd.DataFrame(
                list(
                    tss.values(
                        'account', 'transaction_date', 'transaction_time', 'transaction_id',
                        'deposit_id', 'deposit_amount', 'summary', 'notes'
                    )
                )
            )
            df_tss['last_five'] = df_tss.apply(
                lambda x: x['deposit_id'][-5:], axis=1)

            df_cos['amount_payable'] = 0
            df_cos['amount_payable'] = df_cos.apply(calAP, axis=1)

            df_cos['transfer_amount'] = df_cos['transfer_amount'].fillna(
                0).astype('int')

            df_cos['amount_status'] = df_cos.apply(transferStatus, axis=1)
            df_cos = df_cos.sort_values(
                ['amount_status', 'member__helper__name', 'transfer_amount', 'helper_notes'])

            checkouts = df_cos.T.to_dict().values()

            context['session'] = session
            context['checkouts'] = checkouts
            return render(request, 'reports/memberTransfer.html', context=context)

    def post(self, request):
        postData = request.POST.dict()
        checkout_id = postData['checkout_id']
        helper_notes = postData['helper_notes']

        co = Checkout.objects.get(checkout_id=checkout_id)
        co.helper_notes = helper_notes
        co.save()

        resp = {
            'messages': 'success'
        }

        return HttpResponse(json.dumps(resp), content_type="application/json")


# @user_passes_test(lambda u: u.is_superuser)
# def memberTransfer(request, session_id=None):

@user_passes_test(lambda u: u.is_superuser)
def salesStatistics(request):
    currentSession = Session.objects.get(session_id='20190911')
    ods = Orders.objects.filter(session=currentSession).filter(~Q(amount=0))
    # ods = Orders.objects.filter(session__session_id=session_id).filter(~Q(amount=0))

    # list(ods.values()),objects轉pandas
    df_ods = pd.DataFrame(
        list(ods.values('member_id', 'member__name',
                        'product__wine_id', 'product__name', 'product__product_article_link', 'amount',
                        'product__price', 'product__erp_no')
             )
    )
    df_ods['order_total_price'] = df_ods['amount'] * \
        df_ods['product__price']

    sr = settlementRule.objects.filter(session=currentSession)
    df_sr = pd.DataFrame(
        list(sr.values('wineID', 'wineName', 'price', 'stockNum', 'stockNumFalse', 'limit', 'sale', 'deliverFree')))
    df_sr = df_sr.set_index('wineID')

    df_ods_group = df_ods.groupby(['product__wine_id', 'product__product_article_link'])[
        'amount', 'order_total_price'].sum()
    df_ods_group['bottleCount'] = df_ods.groupby(['product__wine_id', 'product__product_article_link'])[
        'amount'].count()
    df_ods_group = df_ods_group.reset_index().set_index('product__wine_id')

    df = pd.concat([df_ods_group, df_sr], axis=1)
    df['DSR'] = round((df['amount'].astype(int)) /
                      (df['stockNum'].astype(int)) * 100)  # 供需比
    df['bgc'] = ['#fccf80' if i >= 100 else 'white' for i in df['DSR']]
    df['limit'] = df['limit'].apply(lambda s: str(s).replace('0', '無'))
    df['amount'] = df['amount'].astype(int)
    df['stockNum'] = df['stockNum'].astype(int)
    df['price'] = df['price'].astype(int)
    df['saleVal'] = [s if v > s else v for v,
                     s in zip(df['amount'], df['stockNum'])]
    df['settle_total_price'] = df['saleVal'] * df['price']
    df = df.sort_values('DSR', ascending=False)
    df = df.reset_index()
    df = df.rename(columns={'index': 'wine_id'})
    df2 = df.T.to_dict().values()
    context = {
        'session': currentSession,
        'datas': list(df2),
        'total_income': df['settle_total_price'].sum()
    }

    return render(request, 'reports/salesStatistics.html', context=context)


"""
對帳單上傳
"""


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required(login_url='/login/'), name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class BankStatementView(FormView):
    template_name = 'uploadBS.html'
    form_class = BankStatementForm
    success_url = '/upload/'

    def get_context_data(self, **kwargs):
        """Use this to add extra context."""
        context = super(BankStatementView, self).get_context_data(**kwargs)
        context['session_id'] = self.kwargs['session_id']
        return context

    def post(self, request, session_id=None):

        file = request.FILES['file']

        # TODO: 檔案與資料驗證

        self.process_data(file)
        messages.success(request, '資料上傳成功')
        resp = {
            'messages': 'success'
        }

        return HttpResponse(json.dumps(resp), content_type="application/json")

    def process_data(self, file):
        f = io.TextIOWrapper(file, encoding='big5')
        reader = csv.reader(f)
        transactions = list(reader)
        cleaned_transactions = []

        bankAccount = transactions[1][0].replace(
            '="', '').replace(' "', '').replace('"', '')

        tSIdList = BankStatement.objects.filter(
            account=bankAccount).values_list('transaction_id', flat=True)
        timeListQs = BankStatement.objects.filter(
            account=bankAccount)
        timeList = [ts.transaction_time.strftime(
            '%H:%M:%S') for ts in timeListQs]

        for transaction in transactions[1:]:
            cleaned_transaction = [data.replace('="', '').replace(
                '"', '').replace('.00', '').replace("\u3000", '').replace(" ", '').replace("　", '') for data in transaction]

            # 是否已經存在，第八欄是交易序號， 第三項是時間
            isExisted = True if (cleaned_transaction[8] in tSIdList) and (
                cleaned_transaction[3] in timeList) else False

            # 只存匯入的，第七項是提取金額
            if cleaned_transaction[7] and not isExisted:

                # process date
                rocDate = cleaned_transaction[2]
                acYear = int(rocDate[0:3])+1911
                acMonth = int(rocDate[3:5])
                acDay = int(rocDate[5:])
                acDate = datetime.datetime(acYear, acMonth, acDay)
                settings_time_zone = timezone(settings.TIME_ZONE)
                acDate = acDate.astimezone(settings_time_zone)
                cleaned_transaction[2] = acDate

                # process time
                rawTime = cleaned_transaction[3].split(':')
                hour = int(rawTime[0])
                minute = int(rawTime[1])
                sec = int(rawTime[2])
                time = datetime.time(hour, minute, sec)
                cleaned_transaction[3] = time

                cleaned_transactions.append(cleaned_transaction)

        ts = []
        for transaction in cleaned_transactions:

            newBS = BankStatement(
                account=transaction[0],
                transaction_date=transaction[2],
                transaction_time=transaction[3],
                transaction_id=transaction[8],
                deposit_id=transaction[11],
                deposit_amount=transaction[7],
                summary=transaction[9],
                notes=transaction[12]
            )

            ts.append(newBS)

        BankStatement.objects.bulk_create(ts)


"""
發票檔
"""


@user_passes_test(lambda u: u.is_superuser)
def invoice(request, session_id=None):
    context = {
        'allSessions': None,
        'reportType': '發票',
        'reportUrl': 'invoice',
        'session': None,
        'datas': None
    }
    if not session_id:
        allSessions = Session.objects.all().order_by('-year', '-month')
        context['allSessions'] = allSessions
        return render(request, 'reports/invoice.html', context=context)
    else:
        session = Session.objects.get(session_id=session_id)
        ods = Orders.objects.filter(
            session=session).filter(~Q(amount=0)).filter(~Q(minus_free_amount=0))
        df_ods = pd.DataFrame(
            list(
                ods.values(
                    'member_id', 'member__name', 'member__helper__name',
                    'member__shipname', 'member__invoice_id', 'member__invoice_title',
                    'product__wine_id', 'product__name', 'amount', 'minus_free_amount',
                    'product__price', 'notes', 'product__erp_no',

                )
            )
        )

        df_ods['order_total_price'] = df_ods['minus_free_amount'] * \
            df_ods['product__price']
        df_ods = df_ods.sort_values(by=['member_id', 'product__wine_id'])
        orders = df_ods.T.to_dict().values()

        cos = Checkout.objects.filter(session=session)
        df_cos = pd.DataFrame(list(cos.values()))
        checkouts = df_cos.T.to_dict().values()

        allUserInfo = []
        mbids = df_ods.member_id.unique()
        for mb in mbids:
            temp = {
                'orders': None,
                'checkout': None
            }

            orders = df_ods[df_ods['member_id'] == mb]
            checkout = df_cos[df_cos['member_id'] == mb]
            temp['orders'] = list(orders.T.to_dict().values())
            temp['checkout'] = list(checkout.T.to_dict().values())
            total_amount = 0
            for order in temp['orders']:
                total_amount += order['minus_free_amount']
            temp['checkout'][0]['total_amount'] = total_amount
            allUserInfo.append(temp)

        context['session'] = session
        context['datas'] = allUserInfo

        return render(request, 'reports/invoice.html', context=context)


"""
出貨
"""


@user_passes_test(lambda u: u.is_superuser)
def shipment(request, session_id=None):

    context = {
        'allSessions': None,
        'reportType': '出貨明細',
        'reportUrl': 'shipment',
        'session': None,
        'products': None,
        'total_income': None
    }

    if not session_id:
        allSessions = Session.objects.all().order_by('-year', '-month')
        context['allSessions'] = allSessions

        return render(request, 'reports/shipment.html', context=context)
    else:
        session = Session.objects.get(session_id=session_id)
        ods = Orders.objects.filter(
            session=session).filter(~Q(amount=0)).filter(~Q(minus_free_amount=0))
        df_ods = pd.DataFrame(
            list(
                ods.values(
                    'member_id', 'member__name', 'member__shipname',
                    'minus_free_amount', 'member__phone',
                    'member__city', 'member__county', 'member__address',
                    'product__wine_id', 'product__name', 'amount',
                    'product__price', 'notes', 'product__erp_no'
                )
            )
        )

        df_ods['order_total_price'] = df_ods['minus_free_amount'] * \
            df_ods['product__price']
        df_ods = df_ods.sort_values(by=['member_id', 'product__wine_id'])
        orders = df_ods.T.to_dict().values()

        cos = Checkout.objects.filter(session=session)
        df_cos = pd.DataFrame(list(cos.values()))
        checkouts = df_cos.T.to_dict().values()

        allUserInfo = []
        mbids = df_ods.member_id.unique()
        for mb in mbids:
            temp = {
                'orders': None,
                'checkout': None
            }

            orders = df_ods[df_ods['member_id'] == mb]
            checkout = df_cos[df_cos['member_id'] == mb]
            temp['orders'] = list(orders.T.to_dict().values())
            temp['checkout'] = list(checkout.T.to_dict().values())
            total_amount = 0
            for order in temp['orders']:
                total_amount += order['minus_free_amount']
            temp['checkout'][0]['total_amount'] = total_amount
            allUserInfo.append(temp)

        context['session'] = session
        context['datas'] = allUserInfo

        return render(request, 'reports/shipment.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def afterFeeList(request, session_id=None):

    context = {
        'allSessions': None,
        'reportType': '確認購買清單',
        'reportUrl': 'afterFeeList',
        'session': None,
        'datas': None
    }

    if not session_id:
        allSessions = Session.objects.all().order_by('-year', '-month')
        context['allSessions'] = allSessions

        return render(request, 'reports/afterFeeList.html', context=context)
    else:
        session = Session.objects.get(session_id=session_id)
        ods = Orders.objects.filter(
            session=session)
        df_ods = pd.DataFrame(
            list(
                ods.values(
                    'member_id', 'member__fbid', 'member__name', 'member__helper__name',
                    'product__wine_id', 'product__name', 'amount', 'confirm_amount', 'minus_free_amount',
                    'product__price', 'notes', 'product__erp_no'
                )
            )
        )

        df_ods['order_total_price'] = df_ods['minus_free_amount'] * \
            df_ods['product__price']
        df_ods = df_ods.sort_values(by=['member_id', 'product__wine_id'])
        orders = df_ods.T.to_dict().values()

        cos = Checkout.objects.filter(session=session)
        df_cos = pd.DataFrame(list(cos.values()))
        checkouts = df_cos.T.to_dict().values()

        allUserInfo = []
        mbids = df_ods.member_id.unique()
        for mb in mbids:
            temp = {
                'orders': None,
                'checkout': None
            }

            orders = df_ods[df_ods['member_id'] == mb]
            temp['orders'] = list(orders.T.to_dict().values())
            allUserInfo.append(temp)

        context['session'] = session
        context['datas'] = allUserInfo

        return render(request, 'reports/afterFeeList.html', context=context)


"""
隱私權資訊頁面
"""


def terms(request):
    return render(request, 'terms.html')


"""
用戶顯示目前熱門商品
"""


def hotReport(request):
    session_id = '20190911'
    currentSession = Session.objects.get(session_id=session_id)
    # 物件關聯,兩種寫法
    # session = Session.objects.get(session_id=session_id)
    # ods = Orders.objects.filter(session=session).filter(~Q(amount=0))
    ods = Orders.objects.filter(
        session__session_id=session_id).filter(~Q(amount=0))

    # list(ods.values()),objects轉pandas
    df_ods = pd.DataFrame(
        list(ods.values('member_id', 'member__name',
                        'product__wine_id', 'product__name', 'amount', 'product__product_article_link',
                        'product__price', 'product__erp_no')
             )
    )
    df_ods['order_total_price'] = df_ods['amount'] * \
        df_ods['product__price']

    # 提取品項規則
    sr = settlementRule.objects.filter(session=session_id)
    df_sr = pd.DataFrame(
        list(sr.values('wineID', 'wineName', 'price', 'stockNum', 'stockNumFalse', 'limit', 'sale', 'deliverFree')))
    df_sr = df_sr.set_index('wineID')

    df_ods_group = df_ods.groupby(['product__wine_id', 'product__product_article_link'])[
        'amount', 'order_total_price'].sum()
    df_ods_group['bottleCount'] = df_ods.groupby(['product__wine_id', 'product__product_article_link'])[
        'amount'].count()
    df_ods_group = df_ods_group.reset_index().set_index('product__wine_id')
    df = pd.concat([df_ods_group, df_sr], axis=1)
    df['DSR'] = round((df['amount'].astype(int)) /
                      (df['stockNumFalse'].astype(int)) * 100)  # 供需比
    df['limit'] = df['limit'].apply(lambda s: str(s).replace('0', '無'))
    df['bgc'] = ['#fccf80' if i > 100 else 'white' for i in df['DSR']]
    df = df.sort_values('DSR', ascending=False)
    df = df.reset_index()
    df = df.rename(columns={'index': 'wine_id'})
    df2 = df.T.to_dict().values()
    context = {
        'session': currentSession,
        'datas': list(df2)
    }

    return render(request, 'hotReport.html', context=context)
