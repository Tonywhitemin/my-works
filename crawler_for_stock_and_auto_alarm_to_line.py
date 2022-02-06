from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests
import urequests   # 匯入urequests模組
from datetime import datetime
import datetime as dt

url = 'https://histock.tw/index/JNM'
web = webdriver.Chrome('chromedriver.exe')
web.implicitly_wait(60)
web.get(url)
html = web.page_source
open_market_time=dt.datetime(year=2022, month=2, day=6, hour=8, minute=0, second=0) #記得日期要改!!
while True:
    soup=BeautifulSoup(html,'html.parser')
    c_data=soup.find(class_="clr-gr")
    print("及時數值: ",c_data.text)

    #抓開盤價
    sel='#chartInfo_DayK > ul > li:nth-child(2) > div.ci_value'
    o_data=soup.select(sel)
    for d in o_data:
        print("開盤價: ",d.text)

    url_line="http://maker.ifttt.com/trigger/stock/with/key/cb2trxTAfjS21xZy87Q74e"
    if(float(c_data.text)>=float(d.text)-100):  #可設定自己喜歡的公式
        requests.get(url_line+"?value1="+str(c_data.text)) # 傳送至LINE
        print("要進/出場了")
    now=datetime.now()
    delta_time=str(now-open_market_time)
    print(delta_time)
    if delta_time.startswith("8"):
        break
    else:
        time.sleep(5)

web.quit()
