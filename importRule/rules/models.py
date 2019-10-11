from django.db import models

# Create your models here.
class orginalBigSheet(models.Model):
    wineID = models.CharField(max_length=100)
    fbURL = models.URLField(blank=True)
    comment_order = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    fbuid = models.CharField(max_length=100)
    commentTime = models.CharField(max_length=100)
    orderCount= models.CharField(max_length=100)
    crawlDate = models.CharField(max_length=100)
    session = models.CharField(max_length=100)

class settlementRule(models.Model):
    session = models.CharField(max_length=100)
    wineID =  models.CharField(max_length=100)
    erpID = models.CharField(max_length=100,default='NaN')
    price = models.CharField(max_length=100)
    stockNum = models.CharField(max_length=100)
    wineName = models.CharField(max_length=100)
    style = models.CharField(max_length=100)
    deliverFree= models.CharField(max_length=100)
    sale = models.CharField(max_length=100)
    limit = models.CharField(max_length=100)

class deliverRule(models.Model):
    session = models.CharField(max_length=100)
    style =  models.CharField(max_length=100)
    commodityName = models.CharField(max_length=100,)
    deliverRule1 = models.CharField(max_length=100)
    deliverRule1Price = models.CharField(max_length=100)
    deliverRule2 = models.CharField(max_length=100)
    deliverRule2Price = models.CharField(max_length=100)
    deliverRule3 = models.CharField(max_length=100)
    deliverRule3Price = models.CharField(max_length=100)


class deliverFreeAllRule(models.Model):
    session = models.CharField(max_length=100)
    deilverFreeAll =  models.CharField(max_length=100)
    deilverFreeAllbottle= models.CharField(max_length=100)
    discountAll= models.CharField(max_length=100)
