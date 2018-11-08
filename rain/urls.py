"""rain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from demo.views import apiSearch
from demo.views import home
from demo.views import crud

from demo import views


from demo.views import apiListCrud
from demo.views import apiListset
from demo.views import apiListdel
from demo.views import pandasList
# from demo.views import month
from demo.views import crawl_monthly_report
from demo.views import crawl_price
from demo.views import price_list
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('crud', crud),  # 數據操作頁
    path('', home),  # 首頁
    path('search', apiSearch),  # 搜尋api
    path('apiListCrud', apiListCrud),    # 數據操作 api 查詢
    path('apiListset', apiListset),      # 數據操作 api 儲存
    path('apiListdel', apiListdel),      # 數據操作 api 刪除
    path('pandasList', pandasList),      # 股價資訊爬取
    # path('month', month),                # 月營收爬取
    path('crawl_monthly_report', crawl_monthly_report),  # 月營收爬取
    path('crawl_price', crawl_price),       #  每日更新股價
    path('price_list', price_list),         #  財經數據更新

]


