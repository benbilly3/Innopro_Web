from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (settlementRule,deliverRule,deliverFreeAllRule)


@admin.register(settlementRule)
class settlementRuleAdmin(ImportExportModelAdmin):
    list_display = ('id','session','wineID','erpID','price','stockNum','wineName','style','deliverFree','sale','limit')
#,'erpID','price','stockNum','wineName','style','deliverFree','sale','limit'

@admin.register(deliverRule)
class deliverRuleAdmin(ImportExportModelAdmin):
    list_display = ('id','session','style','commodityName','deliverRule1','deliverRule1Price','deliverRule2','deliverRule2Price','deliverRule3','deliverRule3Price')

@admin.register(deliverFreeAllRule)
class deliverFreeAllRuleAdmin(ImportExportModelAdmin):
    list_display = ('id','session','deilverFreeAll','deilverFreeAllbottle')

