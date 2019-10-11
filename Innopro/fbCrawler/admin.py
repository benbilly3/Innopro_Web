from django.contrib import admin
from django.utils.html import format_html
from fbCrawler.models import Product, Members, Orders, Group, Helper, DeliverRule, Session, Checkout, BankStatement

from import_export import resources,widgets
from import_export.fields import Field

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ['wine_id', 'name', 'year', 'month', 'fb_link']
    ordering = ['wine_id', 'year', 'month']
    search_fields = ['wine_id', 'name', 'year', 'month', 'product_fb_link']

    def fb_link(self, instance):
        return format_html(u'<a href="{}" target="_blank">連結</a>'.format(instance.product_fb_link))

    fb_link.short_description = "FB 網址"


class OrderAdmin(admin.ModelAdmin):
    list_display = ('member','product','amount' ,'session')
    search_fields = ('member__name',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(OrderAdmin, self).get_search_results(
            request, queryset, search_term)
        try:
            search_term_as_int = int(search_term)
            queryset |= self.model.objects.filter(member_name__contains=search_term_as_int)
        except:
            pass
        return queryset, use_distinct

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (settlementRule,deliverSettleRule,deliverFreeAllRule,vip)


@admin.register(settlementRule)
class settlementRuleAdmin(ImportExportModelAdmin):
    list_display = ('id','session','wineID','erpID','price','stockNum','stockNumFalse','wineName','style','deliverFree','sale','limit')
#,'erpID','price','stockNum','wineName','style','deliverFree','sale','limit'

@admin.register(deliverSettleRule)
class deliverSettleRuleAdmin(ImportExportModelAdmin):
    list_display = ('id','session','style','commodityName','deliverRule1','deliverRule1Price','deliverRule2','deliverRule2Price','deliverRule3','deliverRule3Price')

@admin.register(deliverFreeAllRule)
class deliverFreeAllRuleAdmin(ImportExportModelAdmin):
    list_display = ('session','deilverFreeAll','deilverFreeAllbottle')

@admin.register(vip)
class vipAdmin(ImportExportModelAdmin):
    list_display = ('session','VIPfbuid','VIPusername','VIPorder','group')

admin.site.register(Product, ProductAdmin)
admin.site.register(Members)
admin.site.register(Orders, OrderAdmin)
admin.site.register(Group)
admin.site.register(Helper)
# admin.site.register(DeliverRule)
admin.site.register(Session)
admin.site.register(Checkout)

# class BankStatementResource(resources.ModelResource):
#         id_session = Field(column_name='field_id_sesion_excel',attribute='id_session')
#         place = Field(column_name='place_field_excel', attribute='place', widget=widgets.ForeignKeyWidget(Contact))

#         class Meta:
#             model = BankStatement
#             skip_unchanged = True

#         def before_import_row(self,row, **kwargs):
#             value = row['place_field_excel']
#             obj = Place.objects.create(id_place=value) #create object place
#             row['place_field_excel'] = obj.id # update value to id ob new object

#         def save_instance(self,instance, using_transactions=True, dry_run=False):
#             try:
#                 instance.save() # inside try for ignore error on duplicate primary keys
#             except Exception as e:
#                 print('update error')
#                 print(e)

    # @admin.register(Session)
    # class SessionAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    #     resource_class = SessionResource