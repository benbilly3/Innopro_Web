from import_export import resources
from .models import (settlementRule,deliverRule,deliverFreeAllRule)

class settlementRuleResource(resources.ModelResource):
    class Meta:
        model = settlementRule

class deliverRuleResource(resources.ModelResource):
    class Meta:
        model = deliverRule

class deliverFreeAllRuleResource(resources.ModelResource):
    class Meta:
        model = deliverFreeAllRule