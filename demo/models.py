from django.db import models
from django.utils import timezone
# Create your models here.
from django_pandas.managers import DataFrameManager


class demo(models.Model):
    title = models.CharField(max_length=100)
    crated_at = models.DateTimeField(default=timezone.now)

    objects = DataFrameManager()
    # def __str__(self):
    #     return self.title

# 每日股價
class price(models.Model):
    date                = models.CharField(max_length=100, help_text='月報時間')
    stock_id            = models.CharField(max_length=100, help_text='證券代號')
    stock_name          = models.CharField(max_length=100, help_text='證券名稱')
    deal_stock_num      = models.CharField(max_length=100, help_text='成交股數')
    deal_num            = models.CharField(max_length=100, help_text='成交筆數')
    deal_amount         = models.CharField(max_length=100, help_text='成交金額')
    open                = models.CharField(max_length=100, help_text='開盤價')
    high          = models.CharField(max_length=100, help_text='最高價')
    low          = models.CharField(max_length=100, help_text='最低價')
    close        = models.CharField(max_length=100, help_text='收盤價')
    spread              = models.CharField(max_length=100, help_text='漲跌價差')
    last_buy_price      = models.CharField(max_length=100, help_text='最後揭示買價')
    last_buy_num        = models.CharField(max_length=100, help_text='最後揭示買量')
    last_sell_price     = models.CharField(max_length=100, help_text='最後揭示賣價')
    last_sell_num       = models.CharField(max_length=100, help_text='最後揭示賣量')
    ratio               = models.CharField(max_length=100, help_text='本益比')
    crated_at           = models.DateTimeField(default=timezone.now)
    update_at           = models.DateTimeField(auto_now =True)
    objects             = DataFrameManager()

# 每月財報
class monthly(models.Model):
    date                            = models.CharField(max_length=100, help_text='月報時間')
    company_id                      = models.CharField(max_length=100, help_text='公司代號')
    company_name                    = models.CharField(max_length=100, help_text='公司名稱')
    now_month                       = models.CharField(max_length=100, help_text='當月營收')
    last_month                      = models.CharField(max_length=100, help_text='上月營收')
    last_year_now_month             = models.CharField(max_length=100, help_text='前年當月營收')
    last_month_contrast             = models.CharField(max_length=100, help_text='上月比較增減')
    last_year_now_month_contrast    = models.CharField(max_length=100, help_text='去年同月增減')
    now_month_total                 = models.CharField(max_length=100, help_text='當月累計營收')
    last_year_total                 = models.CharField(max_length=100, help_text='去年累計營收')
    prophase_contrast               = models.CharField(max_length=100, help_text='前期比較增減')
    crated_at                       = models.DateTimeField(default=timezone.now)
    update_at                       = models.DateTimeField(auto_now =True)
    objects                         = DataFrameManager()