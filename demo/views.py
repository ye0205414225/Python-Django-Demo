from django.http import HttpResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.db import models
from django.http import JsonResponse
from django.core import serializers
import json
import requests
from bs4 import BeautifulSoup
# 爬蟲
from django.views.decorators.csrf import csrf_exempt
# JSON 編譯
import demjson
from io import StringIO

from demo.models import demo
from demo.models import price
from demo.models import monthly

from django_pandas.io import pd
import numpy as np
import datetime


import matplotlib.pyplot as plt
import numpy as np


"""
財經數據更新

"""

def price_list(request):

    response = render(request, 'price_list.html')
    return response



"""
股價資訊爬蟲
"""
@csrf_exempt #  宣告 csrf
def crawl_price(request):

    data = json.loads(request.body)

    thisTime = data['dayStart']

    startYear, startMonth, startDay =  data['dayStart'].split('-')
    endDay = data['dayEnd']
    startDay = int(startDay)
    endDay = int(endDay)

    while (startDay <= endDay):

        datestr = str(startYear)+str(startMonth)+str(startDay)

        try:
            r = requests.post(
                'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALLBUT0999')
        except:

            return None

        startDay = int(startDay) + 1

        content = r.text.replace('=', '')
        lines = content.split('\n')
        lines = list(filter(lambda l: len(l.split('",')) > 10, lines))
        content = "\n".join(lines)
        if content == '':
            return None

        df = pd.read_csv(StringIO(content))
        df = df.astype(str)
        df = df.apply(lambda s: s.str.replace(',', ''))
        df = df[df.columns[df.isnull().all() == False]]
        df = df[~df['收盤價'].isnull()]
        jsonls = df.to_json(orient='table')
        jsonls2 = json.loads(jsonls)
        jsondf = jsonls2['data']

        querysetlist = []

        for listdf in jsondf:
            querysetlist.append(price(
                stock_id= listdf['證券代號'],
                stock_name=listdf['證券名稱'],
                date    = datestr,
                deal_stock_num=listdf['成交股數'],
                deal_num= listdf['成交筆數'],
                deal_amount=listdf['成交金額'],
                open=listdf['開盤價'],
                high=listdf['最高價'],
                low=listdf['最低價'],
                close=listdf['收盤價'],
                spread=listdf['漲跌價差'],
                last_buy_price=listdf['最後揭示買價'],
                last_buy_num=listdf['最後揭示買量'],
                last_sell_price=listdf['最後揭示賣價'],
                last_sell_num=listdf['最後揭示賣量'],
                ratio=listdf['本益比'],
            ))
        price.objects.bulk_create(querysetlist)

    return HttpResponse(startDay)



def pandasList(request):


    #
    # print(s)

    # pd.DataFrameManager

    # qs = demo.objects.all()
    #
    # df = qs.to_dataframe(['id', 'title'], index=['id'])
    #
    # return HttpResponse(df.to_html())
    # json = df.to_json(orient='records')
    #
    # context = {
    #     'data': json,
    #
    # }
    #
    #
    # return JsonResponse(context)

    # 將 date 變成字串 舉例：'20180525'
    # datestr = date.strftime('%Y%m%d')

    # 從網站上依照 datestr 將指定日期的股價抓下來

    response = requests.get('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=20180309&type=ALLBUT0999&_=1520785530355')

    lines = response.text.split('\n')

    lines[100]

    newlines = []

    for line in lines:

        # 用「",」切開每一行，看是否被切成17個
        if len(line.split('",')) == 17:
            # 將 line 加到新的 newlines 中
            newlines.append(line)

    print('原本的行數（lines）')
    print(len(lines))
    print('刪除不需要的行數後，變少了(newlines)')
    print(len(newlines))

    c = '\n'
    # 利用此字元c，將每一行給連在一起
    s = c.join(newlines)
    # 將 s 裡面的 等號 刪除
    s = s.replace('=', '')

    # 將 s 用StringIO變成檔案，並用 pd.read_csv 來讀取檔案
    df = pd.read_csv(StringIO(s))

    df = df.applymap(lambda s: s.replace(',', ''))

    # 將 df 證券代號變成 index
    df = df.set_index('證券代號')

    # 將 df 中的元素從字串變成數字
    df = df.apply(lambda s: pd.to_numeric(s, errors='coerce'))

    # 要刪除沒有用的columns
    # 其中 axis=1 為是說每條columns去檢查有沒有NaN
    # how='all' 是說假如全部都是 NaN 則刪除該 column
    # （原本的方法） df = df[df.columns[df.isnull().sum() != len(df)]]

    df.dropna(axis=1, how='all', inplace=True)

    # 紅棒的長度，1代表不漲不跌，小於一代表收盤價比較小（股價跌），大於一代表收盤價比較大（股票漲）
    close_open = df['收盤價'] / df['開盤價']
    close_open.head(5)
    df[close_open > 1.05]



"""
月報資訊
"""

@csrf_exempt #  宣告 csrf
# 定義月報爬蟲的function
def crawl_monthly_report(request):

    data = json.loads(request.body)

    thisTime = data['monthStart']

    startYear, startMonth, =  data['monthStart'].split('-')
    endMonth = data['monthEnd']

    startMonth = int(startMonth)
    endMonth = int(endMonth)

    while (startMonth <= endMonth):
        # 指定爬取月報的網址（指定特定年份和月份）


        getTime = str(startYear)+'-'+str(startMonth)

        url = 'http://mops.twse.com.tw/nas/t21/sii/t21sc03_' + str(int(startYear) - int(1911)) + '_' + str(startMonth) + '_0.html'

        startMonth = int(startMonth) + 1


        # 偽瀏覽器（讓request能夠偽裝成瀏覽器）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

        # 下載該年月的網站，並用pandas轉換成 dataframe
        r = requests.get(url, headers)
        r.encoding = 'big5'  # 讓pandas可以讀取中文（測試看看，假如不行讀取中文，就改成 'utf-8'）

        # 這裡使用 try 和 except 是因為 dataframe 有可能無法讀取 html 檔，在這樣的情況下，程式就會跑出 None，而不會因為讀取不了而出現 error
        try:
            html_df = pd.read_html(StringIO(r.text))
        except:
            return None

        # 現在開始整理一下資料
        # 我們要先取出從網頁下載下來的 table，但是因為月報網頁的格式會因為日期而有所不同
        # (有些是一個大的總表加上一些重複的小圖表，有些沒有大圖表，只有分散的小圖表)
        # 所以下載下來的圖表需要先經過一些判斷，來決定我們需要取圖表的是哪個！

        # 首先，我們先看看下載下來的第一個圖表的 row 是否大於 500 行，來判斷第一個圖表是不是大總表
        if len(html_df[0]) > 500:

            # 如果是大圖表的話，它就是我們所需要的月報
            df = html_df[0].copy()

        # 如果不是的話，我們就需要把所有的小圖表拼湊成我們需要的月報
        else:

            # 我們先判斷這些小圖表的 column 是否小於等於 11，然後把這些 column 小於 11 的小圖表全部加在一起(.concat) 就是大總表了！
            df = pd.concat([df for df in html_df if df.shape[1] <= 11])

        # 用 list(range(10)) 取 [0,1,2,...,9]，用來選取第0到9個 column
        df = df[list(range(0, 10))]


        # 首先我們可以先取出第0欄為「公司代號」的 rows (df[0] == '公司代號')
        column_index = df.index[(df[0] == '公司代號')][0]

        # 選取 column_index 裡面任意一條 row 當作 column 的名稱 （因為這裡所有的 row 都長的一樣）
        df.columns = df.iloc[column_index]

        # 將 df 中的當月營收用 .to_numeric 變成數字，再把其中不能變成數字的部分以 NaN 取代（errors='coerce'）
        df['當月營收'] = pd.to_numeric(df['當月營收'], errors='coerce')

        # 以 .isnull() 檢查是否為 NaN，再取其否定「～」的行數作為新的 df
        df = df[~df['當月營收'].isnull()]

        # 取「公司代號」中，不是「合計」的行數
        df = df[df['公司代號'] != '合計']

        # 找出下個月的月報出爐日（每個月的10號）
        # next_month = datetime.date(int(startYear) + int(startMonth / 12), ((int(startMonth)  % 12) + 1), 10)
        # df['date'] = pd.to_datetime(next_month)


        # 將 df 中的所有字串轉成數值，並且把其中沒有 NaN 的行數取出
        # df = df.apply(lambda s: pd.to_numeric(s, errors='coerce'))
        # df = df[df.columns[df.isnull().all() == False]]

        print(df)

        jsonls = df[0:].to_json(orient='table')
        jsonls2 = json.loads(jsonls)
        jsondf = jsonls2['data']

        querysetlist = []

        for listdf in jsondf:
            querysetlist.append(monthly(
                date= getTime,
                company_id=listdf['公司代號'],
                company_name=listdf['公司名稱'],
                now_month=listdf['當月營收'],
                last_month=listdf['上月營收'],
                last_year_now_month=listdf['去年當月營收'],
                last_month_contrast=listdf['上月比較增減(%)'],
                last_year_now_month_contrast=listdf['去年同月增減(%)'],
                now_month_total=listdf['當月累計營收'],
                last_year_total=listdf['去年累計營收'],
                prophase_contrast=listdf['前期比較增減(%)'],
            ))

        monthly.objects.bulk_create(querysetlist)
        # startMonth = int(startMonth) + 1

    return HttpResponse('success')

# 實際使用這個 function 試試看！



# def month(request):
#     # 指定爬取月報的網址
#     url = 'http://mops.twse.com.tw/nas/t21/sii/t21sc03_106_1_0.html'
#     # 抓取網頁
#     r = requests.get(url)
#
#     # 讓pandas可以讀取中文（測試看看，假如不行讀取中文，就改成 'utf-8'）
#     r.encoding = 'big5'
#     # 把剛剛下載下來的網頁的 html 文字檔，利用 StringIO() 包裝成一個檔案給 pandas 讀取
#     dfs = pd.read_html(StringIO(r.text))
#
#     # 取出剛剛下載下來的 html 檔案裡面的第一個圖表，通常我們下載下來的第一個圖表 (dfs[0]) 就是月報的總表
#     df = dfs[0]
#
#     # --------------------------------------------- #
#     # 我們用 iloc 來取出所有的 rows  和 前十個 columns  #
#     # --------------------------------------------- #
#
#     # 在 [:,:10] 中，逗點前面指定 row 的 id，逗點後面用來指定 columns 的 id
#     # 用 「:」 代表，這裡的冒號前後都沒有放數字就代表了我們取頭到尾，「:10」，代表我們從第0個開始取到第9個
#     df = df.iloc[:, :10]
#
#     # df = df[list(range(10))] <----影片中的寫法，可以取代上面那行，其中 list(range(10)) 是 [0,1,2,...,9]，用來選取第0到9個 column
#
#     # --------------------- #
#     # 設定正確的 columns 名稱 #
#     # --------------------- #
#
#     # 首先我們可以先取出第0欄為「公司代號」的 rows (df[0] == '公司代號')
#     column_name = df[df[0] == '公司代號']
#
#     # 選取 column_name 裡面任意一條 row 當作 column 的名稱 （因為這裡所有的 row 都長的一樣）
#     df.columns = column_name.iloc[0]
#
#     # 將 df 中的當月營收用 .to_numeric 變成數字，再把其中不能變成數字的部分以 NaN 取代（errors='coerce'）
#     df['當月營收'] = pd.to_numeric(df['當月營收'], errors='coerce')
#     # 再把當月營收中，出現 NaN 的 row 用 .dropna 整行刪除
#     df = df.dropna(subset=['當月營收'])
#
#     # df = df.loc[~pd.to_numeric(df['當月營收'], errors='coerce').isnull()] ---->影片中的寫法，可以取代上面兩行（以 .isnull() 檢查是否為 NaN，再取其否定「～」的行數作為新的 df）
#
#     # 刪除「公司代號」中出現「合計」的行數，其中「～」是否定的意思
#     df = df.loc[~(df['公司代號'] == '合計')]
#
#     # 將「公司代號」與「公司名稱」共同列為 df 的 indexes
#     df = df.set_index(['公司代號', '公司名稱'])
#
#     # 最後，將 df 中的所有字串轉成數值
#     df = df.apply(pd.to_numeric)
#     # # ----------- #
#     # # 存取 csv 檔  #
#     # # ----------- #
#     #
#     # # 把 df 存成 csv 檔，並且命名為「test.csv」，指定用「utf_8_sig」編碼
#     # df.to_csv('test.csv', encoding='utf_8_sig')
#     #
#     # # 讀取名為「test.csv」的 csv 檔，並且指定其中欄位名稱為「公司代號」與「公司名稱」作為 df 的 indexes
#     # df = pd.read_csv('test.csv', index_col=['公司代號', '公司名稱'])
#
#     print(df)
#
#     jsonls = df[0:].to_json(orient='table')
#
#     jsonls2 = json.loads(jsonls)
#     jsondf = jsonls2['data']
#
#     print(jsondf)
#
#     querysetlist = []
#
#     for listdf in jsondf:
#         querysetlist.append(monthly_report(
#             公司代號=listdf['公司代號'],
#             公司名稱=listdf['公司名稱'],
#             當月營收=listdf['當月營收'],
#             上月營收=listdf['上月營收'],
#             去年當月營收=listdf['去年當月營收'],
#             上月比較增減=listdf['上月比較增減(%)'],
#             去年同月增減=listdf['去年同月增減(%)'],
#             當月累計營收=listdf['當月累計營收'],
#             去年累計營收=listdf['去年累計營收'],
#             前期比較增減=listdf['前期比較增減(%)'],
#         ))
#
#     monthly_report.objects.bulk_create(querysetlist)
#
#     return HttpResponse(jsondf)



"""
CRUD-數據操作首頁
"""
def crud(request):


    response = render(request, 'crud.html')
    return response

"""
CRUD-數據操作 查詢list
"""

def apiListCrud(request):


    listdata = demo.objects.values('id', 'title')

    for item in listdata:

        item['title'] = item['title']
        item['checkbox'] = False
        item['edit'] = False

    data = {
        'listData':list(listdata)
    }

    return JsonResponse(data)

"""
 CRUD-數據操作 新增/編輯 list 
"""
@csrf_exempt #  宣告 csrf
def apiListset(request):

    if request.method == 'POST':

        # json格式解析
        data = json.loads(request.body)

        querysetlist = []

        for item in data['setData']:
            if data['setData'][item]['id'] :
                demo.objects.filter(id=data['setData'][item]['id']).update(title=data['setData'][item]['title'])
            else:
                querysetlist.append(demo(title = data['setData'][item]['title']))
                # demo.objects.create(title = data['setData'][item]['title'])
        demo.objects.bulk_create(querysetlist)

        return HttpResponse('success')
    else:
        return HttpResponse('error')




    # 取出來資料轉json
    # gatData = serializers.serialize('json',listdata)

    # return HttpResponse()
    # 轉中文編碼
    # myjson = json.loads(gatData)
    # data = json.dumps(myjson, ensure_ascii=False)
    # return JsonResponse({'data': gatData })

"""
 CRUD-數據操作 刪除list 
"""
@csrf_exempt #  宣告 csrf

def apiListdel(request):

    if request.method == 'POST':

        data = json.loads(request.body)

        delArr = {}

        for item in data['delData']:

            delArr[data['delData'][item]['id']] = True


        demo.objects.filter(id__in = delArr).delete()

        return HttpResponse('success')

    else:
        return HttpResponse('error')



def home(request):

    response = render(request, 'home.html')
    return response



"""
CRUD-數據操作首頁
"""
def crud(request):


    response = render(request, 'crud.html')
    return response




"""
@param   type:json  request:keyWord     [post關鍵字]
@return  type:json  var:obj             [回傳數據]
"""
@csrf_exempt #  宣告 csrf

def apiSearch(request):

    # 判斷是否為請求資料
    if request.method == 'POST':
        # json格式解析
        data = json.loads(request.body)
        # json格式抓出key
        result = json.dumps(data['keyWord'])
        # 解析
        keyWord = demjson.decode(result)
    else:
        # 預設
        keyWord = '小春tv'

    # 連結
    youtubeURL = 'https://www.youtube.com/results?search_query='+keyWord


    res = requests.get(youtubeURL)
    content = res.content

    # 爬蟲函式
    soup = BeautifulSoup(content, "html.parser")


    # keyWord
    for all_mv in soup.select(".item-section"):

        listData = all_mv.select(".yt-lockup-dismissable")

    # 起數
    i = 0
    # 抓出比數
    num = 12
    # 宣告物件 存陣列用
    obj = {}
    for content in listData:
        # 如果到第12比跳出迴圈
        if i == num:
            break
        # 判斷沒有的條件
        if content.select(".formatted-video-count-label"):
            0
        else:

            if content.select("img")[0].get('src') != '/yts/img/pixel-vfl3z5WfW.gif':
                img = content.select("img")[0].get('src')
            else:
                img = content.select("img")[0].get('data-thumb')

            string = content.select(".yt-uix-sessionlink")[0].get('href')

            # isinstance = 判斷型態
            if content.select(".video-time"):
                Time = content.select(".video-time")[0].string
            else:
                Time = False



            obj[i] = {
                'videoTitle': content.select(".yt-lockup-title a")[0].get('title'),
                'videoImg': img,
                'videoTime': Time,
                'videoUrl':  string[9:]
            }

            i+=1

    return JsonResponse({'data':obj })