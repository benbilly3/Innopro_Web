"""Innopro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


from django.conf import settings
from django.conf.urls.static import static

# path('', RedirectView.as_view(url=reverse_lazy('admin:index'))),
# from django.urls import path, reverse_lazy
# from django.views.generic.base import RedirectView

# from django.contrib.auth.views import LoginView
from fbCrawler import views

from django.views.decorators.cache import cache_page


"""
Basics
"""
urlpatterns = [
    path('', views.index),
    path('admin/', admin.site.urls, name='index'),
    path('login/', views.MemberLoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout')
]
# cache_page(60 * 5)

"""
小幫手處理
"""
urlpatterns += [
    # path('members/', views.members, name='membersAll'),
    path('members/', views.members, name='membersAll'),
    path('members/<str:year>/<str:month>', views.members, name='members_date'),
    path('members/<str:fbuid>/', views.members, name='memberAll'),
    path('members/<str:fbuid>/<str:year>/<str:month>',
         views.members, name='member_date'),
    path('memberTransfer/', views.MemberTransferView.as_view(), name='memberTransferAll'),
    path('memberTransfer/<int:session_id>',
         views.MemberTransferView.as_view(), name='memberTransfer'),
    path('items/', views.items, name='items_home'),
    path('items/<str:year>/<str:month>/', views.items, name='items'),
    path('bigtable/', views.bigtable, name='bigtableAll'),
    path('bigtable/<int:session_id>', views.bigtable, name='bigtable'),
    path('sales/', (views.sales), name='salesAll'),
    path('sales/<int:session_id>', (views.sales), name='sales'),
    path('salesStatistics/', views.salesStatistics, name='salesStatisticsAll'),
    path('salesStatistics/<int:session_id>',
         views.salesStatistics, name='salesStatistics'),
    path('invoice/', views.invoice, name='invoiceAll'),
    path('invoice/<int:session_id>', views.invoice, name='invoice'),
    path('shipment/', views.shipment, name='shipmentAll'),
    path('shipment/<int:session_id>', views.shipment, name='shipment'),
    path('afterFeeList/', views.afterFeeList, name='afterFeeListAll'),
    path('afterFeeList/<int:session_id>',
         views.afterFeeList, name='afterFeeList'),
    path('hotReport/', views.hotReport, name='hotReport'),
]

"""
Session 相關
"""
urlpatterns += [
    path('session/', views.SessionView.as_view(), name='sessioIndex'),
    path('session/<str:session_id>', views.SessionView.as_view(), name='session'),
    path('session/<str:session_id>/updateOrder/',
         views.sessionUpdateOrderView.as_view(), name='sessionUpdateOrder'),
    path('session/<str:session_id>/confirmedOrder/',
         views.sessionConfirmedOrder.as_view(), name='sessionConfirmedOrder'),
    path('updateOrder/', views.updateOrder, name='updateOrder_default'),
    path('updateOrder/<str:fbuid>/', views.updateOrder, name='updateOrder'),
    path('confirmedOrder/', views.confirmedOrder, name='confirmedOrder_default'),
    path('confirmedOrder/<str:fbuid>/',
         views.confirmedOrder, name='confirmedOrder'),
    path('fbUrlToId/', views.fbUrlToId, name='fbUrlToId'),
    path('submitUpdateOrder/', views.submitUpdateOrder, name='submitUpdateOrder'),
    path('submitTransferInfo/', views.submitTransferInfo,
         name='submitTransferInfo'),
]

"""
其他
"""
urlpatterns += [
    path('terms/', views.terms, name='terms'),
    path('temp/', views.sessionConfirmedOrder.as_view(), name='temps'),
    path('temp/<str:session_id>', views.sessionConfirmedOrder.as_view(), name='temp'),
    path('uploadBS/', views.BankStatementView.as_view(), name='uploadBS')
]

# 讓 Heroku 上面可以讀 static 資料夾裡面的內容
urlpatterns + static(settings.STATIC_URL,
                     document_root=settings.STATICFILES_DIRS)
