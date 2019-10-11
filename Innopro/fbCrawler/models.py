from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum

# Create your models here.
# 如果有使用 FK 加上 db_constraint=False 防止資料庫欄位綁定


class Group(models.Model):
    name = models.CharField(
        blank=True, null=True, max_length=100, verbose_name="FB 社團名稱")
    url = models.URLField(
        blank=False, max_length=200, verbose_name="FB Group url")
    group_id = models.CharField(
        blank=True, max_length=100, null=True, verbose_name="社團代碼")

    def __str__(self):
        return str(self.name)


class Members(models.Model):
    user = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(blank=False, max_length=50, verbose_name="用戶名稱")
    fbid = models.CharField(blank=False, max_length=50, verbose_name="FB ID")
    fb_login_app_id = models.CharField(
        blank=True, null=True, max_length=50, verbose_name="FB 登入 App ID")
    user_profile_url = models.URLField(
        blank=True, null=True, max_length=200, verbose_name="FB url")
    is_admin = models.BooleanField(
        blank=False, default=False, verbose_name="是否為管理員")
    helper = models.ForeignKey(
        "Helper", blank=True, null=True, on_delete=models.SET_NULL, db_constraint=False)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(
        blank=True, null=True, max_length=200, verbose_name="地址")
    city = models.CharField(blank=True, null=True,
                            max_length=50, verbose_name="城市")
    county = models.CharField(blank=True, null=True,
                              max_length=50, verbose_name="區")
    zipcode = models.CharField(blank=True, null=True, max_length=10)
    phone = models.CharField(blank=True, null=True,
                             max_length=30, verbose_name="電話")
    shipname = models.CharField(
        blank=True, null=True, max_length=100, verbose_name="收件人")
    invoice_id = models.CharField(
        blank=True, null=True, max_length=50, verbose_name="發票號碼")
    invoice_title = models.CharField(
        blank=True, null=True, max_length=100, verbose_name="發票抬頭")
    group = models.ForeignKey(
        "Group", blank=True, null=True, on_delete=models.SET_NULL, db_constraint=False)
    join_date = models.DateTimeField(
        auto_now=False, blank=True, null=True, verbose_name="加入社團時間")
    created_at = models.DateTimeField(auto_now=True, verbose_name="創建時間")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="更新時間")

    @property
    def tax_type(self):
        if self.invoice_title:
            return 1
        return 2

    def orders(self):
        return Orders.objects.filter(member=self)

    def __str__(self):
        return str(self.name + ' '+self.fbid)


class Helper(models.Model):
    name = models.CharField(blank=False, max_length=50, verbose_name="小幫手名稱")
    fbid = models.CharField(blank=False, max_length=50,
                            verbose_name="小幫手 Fb id")
    user_profile_url = models.URLField(
        blank=False, max_length=200, verbose_name="小幫手 FB url")
    work_percent = models.IntegerField(blank=False, verbose_name="小幫手工作比例")
    bank_account_no = models.CharField(
        blank=True, max_length=50, verbose_name="小幫手帳戶號碼")
    bank_account_title = models.CharField(
        blank=True, max_length=100, verbose_name="小幫手帳戶戶名")
    bank_account_branch = models.CharField(
        blank=True, max_length=100, verbose_name="小幫手帳戶分行")

    def __str__(self):
        return str(self.name)


class Product(models.Model):
    # 感覺 pid 是從外部 ERP 系統傳進來的參數
    pid = models.CharField(blank=True, null=True,
                           max_length=50, verbose_name="產品ID")
    wine_id = models.CharField(blank=False, max_length=20)
    year = models.IntegerField(blank=False, null=True, verbose_name="上架年份")
    month = models.IntegerField(blank=False, null=True, verbose_name="上架月份")
    session = models.ForeignKey(
        "Session", blank=True, null=True, on_delete=models.SET_NULL, db_constraint=False)
    product_fb_link = models.URLField(
        blank=True, null=True, verbose_name="FB 原始 Po 文連結")
    product_article_link = models.URLField(
        blank=True, null=True, verbose_name="FB 備份連結（禁止抄襲社團）")
    erp_no = models.CharField(blank=True, null=True, max_length=50)
    name = models.CharField(blank=False, max_length=200, verbose_name="產品名稱")
    quantity = models.IntegerField(blank=True, null=True, verbose_name="數量")
    order_limit = models.IntegerField(
        blank=True, null=True, verbose_name="購買數量限制")
    style = models.IntegerField(blank=True, null=True)
    deliver_free = models.IntegerField(blank=True, null=True)
    sale = models.IntegerField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True, verbose_name="價錢")
    available = models.BooleanField(default=True, verbose_name="上架")
    post_time = models.DateTimeField(
        blank=True, null=True, verbose_name="創建時間")
    available_at = models.DateTimeField(
        blank=True, null=True, verbose_name="上架時間")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="修改時間")

    def __str__(self):
        return str(self.wine_id + ' ' + self.name)


class Orders(models.Model):
    member = models.ForeignKey(
        "Members", on_delete=models.CASCADE, db_constraint=False)
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, db_constraint=False)
    session = models.ForeignKey(
        "Session", blank=True, null=True, on_delete=models.SET_NULL, db_constraint=False)
    amount = models.IntegerField(blank=False, verbose_name="下單數量")
    confirm_amount = models.IntegerField(
        blank=True, null=True, verbose_name="結算完數量")
    free_amount = models.IntegerField(
        blank=True, null=True, verbose_name="優惠贈送數量")
    minus_free_amount = models.IntegerField(
        blank=True, null=True, verbose_name="扣除贈送量後計價數")
    commented_at = models.DateTimeField(
        blank=True, null=True, verbose_name="留言時間")
    comment_order = models.IntegerField(
        blank=True, null=True, verbose_name="留言順序")
    is_confrimed = models.BooleanField(default=False, verbose_name="是否購買到")
    fb_comment_content = models.TextField(
        blank=True, null=True, verbose_name="留言內文")
    created_at = models.DateTimeField(auto_now=True, verbose_name="創建時間")
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name="更新時間")
    notes = models.TextField(blank=True, null=True, verbose_name="備註")

    @property
    def orderTotalPrice(self):
        return int(self.minus_free_amount * self.product.price) if self.minus_free_amount else 0

    def __str__(self):
        return str(self.member.name + " " + self.product.name + " " + self.session.session_id)


class DeliverRule(models.Model):
    name = models.CharField(blank=False, max_length=50, verbose_name="運費規則名稱")
    commodity = models.CharField(
        blank=True, max_length=50, verbose_name="商品名稱")
    deliver_rule1 = models.IntegerField(
        blank=True, null=True, verbose_name="運費門檻 1")
    deliver_rule1_price = models.IntegerField(
        blank=True, null=True, verbose_name="運費門檻 1 價錢")
    deliver_rule2 = models.IntegerField(
        blank=True, null=True, verbose_name="運費門檻 2")
    deliver_rule2_price = models.IntegerField(
        blank=True, null=True, verbose_name="運費門檻 2 價錢")
    deliver_rule3 = models.IntegerField(
        blank=True, null=True, verbose_name="運費門檻 3")
    deliver_rule3_price = models.IntegerField(
        blank=True, null=True, verbose_name="運費門檻 3 價錢")

    def __str__(self):
        return str(self.name)


class SessionState(object):
    """
    Session狀態

    open: 開放 +1、點讚
    update_orders: 用戶更新訂單數量
    system_update: 系統爬蟲、結算購買權進行中
    checkout: 結帳，填寫匯款資訊
    closed: 已結團
    """

    OPEN = 'open'
    UPDATE_ORDERS = 'update_orders'
    SYSTEM_UPDATING = 'system_updating'
    CHECKOUT = 'checkout'
    CLOSED = 'closed'

    CHOICES = (
        (OPEN, '進行中'),
        (UPDATE_ORDERS, '用戶更新訂單'),
        (SYSTEM_UPDATING, '系統計算中'),
        (CHECKOUT, '用戶匯款'),
        (CLOSED, '已結團'),
    )


class Session(models.Model):
    session_id = models.CharField(
        blank=False, max_length=50, verbose_name="團次編號")
    group = models.ForeignKey(
        "Group", blank=True, null=True, on_delete=models.SET_NULL, db_constraint=False)
    deliver_rule = models.ForeignKey(
        "DeliverRule", blank=True, null=True, on_delete=models.SET_NULL, db_constraint=False)
    year = models.IntegerField(blank=False, null=True, verbose_name="團次年份")
    month = models.IntegerField(blank=False, null=True, verbose_name="團次月份")
    status = models.CharField(default=SessionState.OPEN, max_length=20,
                              choices=SessionState.CHOICES, verbose_name="團次狀態")
    update_announcement = models.TextField(
        blank=True, null=True, verbose_name="開放清單公告")
    transfer_announcement = models.TextField(
        blank=True, null=True, verbose_name="匯款公告")

    @property
    def status_zh(self):
        if self.status == 'open':
            return '進行中'
        elif self.status == 'update_orders':
            return '用戶更新訂單'
        elif self.status == 'system_updating':
            return '系統計算中'
        elif self.status == 'closed':
            return '已結團'
        else:
            return '用戶匯款'

    def __str__(self):
        return str(self.session_id)


class Checkout(models.Model):
    session = models.ForeignKey(
        "Session", on_delete=models.CASCADE, db_constraint=False)
    member = models.ForeignKey(
        "Members", on_delete=models.CASCADE, db_constraint=False)
    checkout_id = models.CharField(
        blank=True, max_length=100, null=True, verbose_name="訂單編號")
    ship_method = models.CharField(
        blank=True, max_length=50, null=True, default='ship', verbose_name="取貨方式")
    # tp/tc/ship
    ship_time = models.CharField(
        blank=True, max_length=50, null=True, default='all', verbose_name="配送時段")
    # morning/ noon/ all
    ship_date = models.CharField(
        blank=True, max_length=100, null=True, verbose_name="指定配送日期")
    price_before_disc = models.IntegerField(
        blank=True, null=True, verbose_name="折扣前總價")
    price_after_disc = models.IntegerField(
        blank=True, null=True, verbose_name="折扣後總價")
    ship_fee = models.IntegerField(blank=True, null=True, verbose_name="運費")
    amount_payable = models.IntegerField(
        blank=True, null=True, verbose_name="應付款項")
    total_price = models.IntegerField(
        blank=True, null=True, verbose_name="含運費價錢")
    transfer_amount = models.IntegerField(
        blank=True, null=True, verbose_name="已匯款金額")
    transfer_account = models.CharField(
        blank=True, max_length=20, null=True, verbose_name="轉出帳號末五碼")
    transfer_time = models.DateTimeField(
        auto_now=False, blank=True, null=True, verbose_name="匯款時間")
    delivery_batch = models.CharField(
        blank=True, max_length=100, null=True, verbose_name="出貨批次")
    notes = models.CharField(
        blank=True, max_length=100, null=True, verbose_name="備註")
    helper_notes = models.CharField(
        blank=True, max_length=200, null=True, verbose_name="小幫手備註")
    quantity_sum = models.IntegerField(
        blank=True, null=True, verbose_name="本期確認購買瓶數")

    @property
    def orderSum(self):
        ordersInThisCO = Orders.objects.filter(
            session=self.session, member=self.member).aggregate(
                Sum('minus_free_amount'))['minus_free_amount__sum']
        return ordersInThisCO

    def payable_amount(self):
        return self.price_after_disc + self.ship_fee if self.ship_method == 'ship' else self.price_after_disc

    def __str__(self):
        return (str(self.session.session_id) + ' ' + self.member.name)


class settlementRule(models.Model):
    session = models.CharField(max_length=100)
    wineID = models.CharField(max_length=100)
    erpID = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    stockNum = models.CharField(max_length=100)
    stockNumFalse = models.CharField(max_length=100)
    wineName = models.CharField(max_length=100)
    style = models.CharField(max_length=100)
    deliverFree = models.CharField(max_length=100)
    sale = models.CharField(max_length=100)
    limit = models.CharField(max_length=100)


class deliverSettleRule(models.Model):
    session = models.CharField(max_length=100)
    style = models.CharField(max_length=100)
    commodityName = models.CharField(max_length=100,)
    deliverRule1 = models.CharField(max_length=100)
    deliverRule1Price = models.CharField(max_length=100)
    deliverRule2 = models.CharField(max_length=100)
    deliverRule2Price = models.CharField(max_length=100)
    deliverRule3 = models.CharField(max_length=100)
    deliverRule3Price = models.CharField(max_length=100)


class deliverFreeAllRule(models.Model):
    session = models.CharField(max_length=100)
    deilverFreeAll = models.CharField(max_length=100)
    deilverFreeAllbottle = models.CharField(max_length=100)
    discountAll = models.CharField(max_length=100)


class BankStatement(models.Model):
    session = models.ForeignKey(
        "Session", blank=True, null=True, on_delete=models.SET_NULL, db_constraint=False)
    account = models.CharField(
        max_length=100, blank=False, null=False, verbose_name="帳號")
    transaction_date = models.DateField(
        auto_now=False, blank=False, null=False, verbose_name="交易日期")
    transaction_time = models.TimeField(
        auto_now=False, blank=False, null=False, verbose_name="交易時間")
    transaction_id = models.CharField(
        max_length=100, blank=False, null=False, verbose_name="交易序號")
    deposit_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="存匯代號")
    deposit_amount = models.IntegerField(
        blank=False, null=False, verbose_name="存入金額")
    summary = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="摘要")
    notes = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="附註")

class vip(models.Model):
    session = models.CharField(max_length=100)
    VIPfbuid= models.CharField(max_length=100)
    VIPusername = models.CharField(max_length=100)
    VIPorder = models.CharField(max_length=100)
    group = models.CharField(max_length=100)