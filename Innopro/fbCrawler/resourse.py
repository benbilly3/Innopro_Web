from import_export import resources
from .models import (settlementRule,deliverSettleRule,deliverFreeAllRule,vip)

class settlementRuleResource(resources.ModelResource):
    class Meta:
        model = settlementRule

class deliverSettleRuleResource(resources.ModelResource):
    class Meta:
        model = deliverSettleRule

class deliverFreeAllRuleResource(resources.ModelResource):
    class Meta:
        model = deliverFreeAllRule

class vipResource(resources.ModelResource):
    class Meta:
        model = vip