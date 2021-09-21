#此頁面參考app2_link.py

from flask import Flask #載入FLASK
from flask import request #載入request物件
from flask import redirect
from flask import render_template #載入render_template
import urllib.request as req
import bs4
import pandas as pd
import xlsxwriter #轉存成excel時可以防止內部有不可辨識的錯誤碼
import os
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import jieba
import numpy as np
#from openpyxl import * #先不要import這行，會產生相容問題...
import xlwings as xw  #jobs_and_commpanies.xlsx前處理用

#=============執行前先將上一次跑的csv/xlsx檔案給刪除=============
to_be_deleted_csv_files = glob.glob('static/*.csv')

for file in to_be_deleted_csv_files:
    try:
        os.remove(file)
    except OSError as e:
        print(f"Error:{ e.strerror}")

to_be_deleted_xlsx_files = glob.glob('static/*.xlsx')

for file in to_be_deleted_xlsx_files:
    try:
        os.remove(file)
    except OSError as e:
        print(f"Error:{ e.strerror}")
#=============以下開始寫Flask============
app=Flask(
    __name__,
    static_folder="static", #靜態檔案儲存資料夾，包含跑出的excel/csv檔都在此路徑
    static_url_path="/static") 
#=============首頁============
@app.route("/",methods=["GET"]) #使用get方法
def index():
    return render_template("index.html") #登錄系統首頁時呈現該html排版

#=============爬蟲，主要與index.html對應============
@app.route("/WebSite",methods=["GET"])

def getData():
    page=request.args.get("page","") #從index.html輸入搜尋頁數時抓取數字
    page=int(page) #轉換成整數(只是好習慣)
    areaCode=request.args.get("areaCode","") #從index.html輸入搜尋區域時抓取字串
    if areaCode=="台北市": #將地區轉為網址的對應碼
        areaCode="6001001000"
    elif areaCode=="新北市":
        areaCode="6001002000"
    elif areaCode=="桃園市":
        areaCode="6001005000"
    elif areaCode=="基隆市":
        areaCode="6001004000"

    for i in range(1,page+1): #抓取多頁資料迴圈
        pageurl="https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword=python&expansionType=job&area="+str(areaCode)+"&order=15&asc=0&page="+str(i)+"&mode=s&jobsource=2018indexpoc"
       
        #讓我們登入更像一般瀏覽器上網
        req_for_header=req.Request(pageurl,headers={
        "User_Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"})
        #解析原始碼
        with req.urlopen(req_for_header) as response:
            data=response.read().decode("utf-8")

        root=bs4.BeautifulSoup(data,"html.parser") #使用beautifulsoup解析

        #==============以下開始爬蟲================
        #爬蟲:職稱與公司名稱
        companies=root.find_all("a",target="_blank")
        for company in companies:
            fileOb = open('static/jobs_and_commpanies.csv','a',encoding='UTF-16') #開啟檔案，若沒有該檔案會自動生成,UTF-16才可以被excel 2007解讀成中文...
            fileOb.write(company.text+",,") #使用.text可以避開104原始碼中的<em>關鍵字標籤，21/7/16克服關鍵字爬蟲問題(原本使用.string)
            fileOb.close() #釋放資源

        #爬蟲:職稱
        descriptions=root.find_all("p",class_="job-list-item__info b-clearfix b-content")
        jobs=root.find_all("a",target="_blank",class_="js-job-link")
        for job in jobs:
            job_tmp = str(job.text).replace('\r','').replace('\n','').replace(",","/").strip() #與Isaac老師討論可以避開原始碼換行的爬蟲問題，對於csv排版有幫助
            fileOb = open('static/jobs.csv','a',encoding='UTF-16')
            fileOb.write(job_tmp+"\n")#每筆資料換行紀錄
            fileOb.close()
        
        #爬蟲:職務描述
        for description in descriptions:
            tmp = str(description.text).replace('\r','').replace('\n','').replace("\t","").replace(",","/").replace('-','').replace('+','').strip()#把原始碼當中已經被換行的東西取消掉的打法
            #如果strip()的引數為空，那麼會預設刪除字串頭和尾的空白字元(包括\n，\r，\t這些)
            #/r/n是回车换行.相当于在记事本里面输入Enter.
            #/t是制表符.相当于再记事本里面输入Tab
            fileOb = open('static/description.csv','a',encoding='UTF-16') 
            fileOb.write(tmp+"\n")
            fileOb.close()
    

    #=============爬蟲完畢，開始做資料的前處理=============
    #先處理merge前要用的第一部分:公司名稱與職稱
    ds=pd.read_csv("static/jobs_and_commpanies.csv",sep=",,",encoding="UTF-16",error_bad_lines=False)
    ds.reset_index()
    ds.columns=["職稱","公司名稱"] #增加欄位名稱
    ds.to_excel("static/jobs_and_commpanies.xlsx")#從csv轉存為xlsx
    
   
    #以下為21/07/20新增程式碼:整理jobs_and_commpanies.xlsx原本很糟糕的格式
    wb = xw.Book('static/jobs_and_commpanies.xlsx') #xw為前面import xlwings，可以刪除多餘不要的columns
    sht = wb.sheets[0] #選定檔案內第一個活頁(工作表1)
    sht.range('A:B').api.Delete() #刪除檔案內A與B欄
    wb.save() #存檔，可以在save()中輸入需另存的檔名
    wb.close() #缺點:會開啟excel，要手動關掉

    # 刪除欄位中有空白列的語法(上面那段處理欄，這裡處理列)
    df = pd.read_excel('static/jobs_and_commpanies.xlsx')
    df.dropna(
        axis=0,
        how='all', #關鍵參數，另一個參數是any，但all是我們要的
        thresh=None,
        subset=None,
        inplace=True)
    df.to_excel('static/jobs_and_commpanies.xlsx')
    
    #以下兩段是為了要在merge以前讓ID欄位可以與merge_jobs_and_des.xlsx對稱
    #小技巧:每次pd.read都會生成一欄位index，借用這點可以讓期望資料merge前達到資料筆數一至的作用
    pre_processing=pd.read_excel("static/jobs_and_commpanies.xlsx")
    pre_processing.columns=["ID","職稱","公司名稱"]
    pre_processing.to_excel("static/jobs_and_commpanies.xlsx")

    pre_processing=pd.read_excel("static/jobs_and_commpanies.xlsx")
    pre_processing.columns=["ID","不要的欄位","職稱","公司名稱"]#之所以會有"不要的欄位"就是因為資料流水號沒有完全對齊(前面處理掉空白列時導致跳號)
    pre_processing.to_excel("static/jobs_and_commpanies.xlsx")

    #=============資料的前處理part 2=============
    #以下開始處理另一個merge要用的檔案:職務描述

    ds1=pd.read_csv("static/description.csv",encoding="UTF-16",error_bad_lines=False)
    ds1.reset_index(col_level=0)
    ds1.columns=["職務描述"]
    ds1.to_csv("static/description02.csv",encoding="UTF-16")

    ds2=pd.read_csv("static/jobs.csv",encoding="UTF-16",error_bad_lines=False)
    ds2.columns=["職稱"]
    ds2.reset_index(col_level=0)
    ds2.to_csv("static/jobs02.csv",encoding="UTF-16")
    
    #讓職稱與職務描述先合併成一個檔案(基於ID)，21/6/20有撈過10頁的數據，jobs02.csv跟description02.csv列數是一致的205行
    merge_source1=pd.read_csv("static/jobs02.csv",sep=",",encoding="UTF-16")
    merge_source1.columns=["ID","職稱"]
    merge_source2=pd.read_csv("static/description02.csv",sep=",",encoding="UTF-16")
    merge_source2.columns=["ID","職務描述"]

    MergeStart=pd.merge(merge_source1,merge_source2,on="ID")
    MergeStart.to_excel("static/merge_jobs_and_des.xlsx",encoding="UTF-16",engine='xlsxwriter')#engine='xlsxwriter'可以防止內部有不可辨識的錯誤碼

    #=============資料的前處理part 3，將前面兩個xlsx檔案做merge=============
    merge_source3=pd.read_excel("static/jobs_and_commpanies.xlsx")
    merge_source4=pd.read_excel("static/merge_jobs_and_des.xlsx")

    MergeStart_step2=pd.merge(merge_source3,merge_source4,on="ID",how="right")[["ID","公司名稱","職稱_x","職務描述","Unnamed: 0_x","職稱_y","Unnamed: 0_y","不要的欄位"]]#將merge的columns做排序
    MergeStart_step2.reset_index(col_level=0)
    MergeStart_step2.columns=["ID","公司名稱","職稱","職務描述","職務描述Jieba","merge比對用職稱","No_Need_Data1","No_Need_Data2"] 
    #上面這行先預留"職務描述Jieba"以便下面那段填入
    MergeStart_step2.to_excel("static/Final_merge.xlsx",encoding="UTF-16")
    
    
    #=============用Jieba處理職務描述的內容=============
    counter=0
    source=pd.read_excel("static/Final_merge.xlsx")
    a=len(source)
    while counter<a:
        Needdata=source.職務描述.iloc[counter]
        #seg_list=jieba.cut(Needdata,cut_all=False) 
        #seg_list=jieba.cut(Needdata,cut_all=True) 
        seg_list=jieba.cut_for_search(Needdata) #7/29評估此方式做斷句比較恰當
        source.職務描述Jieba.iloc[counter]=str("/".join(seg_list)) 
        counter=counter+1
    source.to_excel("static/Final_merge_with_jieba.xlsx")
    

    #=============刪除[公司名稱/職務描述]完全相同的欄位===========
    duplicated_data = pd.DataFrame(pd.read_excel('static/Final_merge_with_jieba.xlsx','Sheet1'))
    wp = duplicated_data.drop_duplicates(['職務描述Jieba',"公司名稱"])
    wp.reset_index(col_level=0)
    wp.to_excel("static/suggestion_system.xlsx")
    #=============================================
    #21/07/26以下為將suggestion_system.xlsx多餘的行列去掉以供download下來給使用者查詢ID時頁面較為簡潔使用
    wb = xw.Book('static/suggestion_system.xlsx')
    sht = wb.sheets[0]
    sht.range('A:C').api.Delete()
    sht.range('E:K').api.Delete()
    wb.save("static/for_download.xlsx")
    wb.close()
    #=============================================
    
    
    return render_template("result.html") #資料處理完以後呈現result.html頁面


#以下對應result.html頁面，先處理TFIDF後依據前端輸入的資料回饋資料給前端
@app.route("/Suggestion",methods=["GET"])
def sugg():
    #=============開始做TFIDF分析=============

    tfidf_source=pd.read_excel("static/suggestion_system.xlsx")
    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b",max_df=0.6,min_df=0.1, stop_words=["是", "的","我","你"]) #參考jieba_test.py
    #如果未加token_pattern=r"(?u)\b\w+\b"的話，會有發生當只有一個中文字的時候會被濾掉
    tfidf_des = vectorizer.fit_transform(tfidf_source['職務描述Jieba']) #用職務描述Jieba欄位做TFIDF分析

    # comping cosine similarity matrix using linear_kernal of sklearn
    cosine_sim_des = linear_kernel(tfidf_des, tfidf_des) #算出相似矩陣

    results = {}

    for idx, row in tfidf_source.iterrows(): #iterrows會輸出每一行的index與對應欄位的列資料
        similar_indices = cosine_sim_des[idx].argsort()[:-50:-1] #argsort()會按照數值大小的"index"值做輸出
        similar_items = [(cosine_sim_des[idx][i],tfidf_source['職稱'][i],tfidf_source['公司名稱'][i],tfidf_source['職務描述'][i]) for i in similar_indices]
        #上面這行是為了後面可以在resukt.html頁面中呈現職稱/公司名稱/職務描述等項目
        results[row['ID']] = similar_items[1:] #similar_items[1:] 之所以要從1:開始就是因為相似值最高的就是自己，要避免輸出此值
    
    #==========從result.html中輸入的資料，對應suggestion_system.xlsx回饋在"搜尋結果"中==========
    ID=request.args.get("ID","") #使用者輸入ID值抓進來取得資料
    ID=int(ID)
    #以下兩行為在前端呈現使用者從for_download.xlsx所選ID對應的職稱與公司名稱的資料
    search_job_title=tfidf_source.loc[tfidf_source['ID'] == ID]['職稱']
    search_comp=tfidf_source.loc[tfidf_source['ID'] == ID]["公司名稱"]
    
    #以下兩行為呈現使用者輸入期望推薦筆數的資料回饋
    suggestion_num=request.args.get("suggestion_num","")
    suggestion_num=int(suggestion_num)
    
    #基於以上使用者輸入的"ID"與"推薦筆數"回饋資料到"搜尋結果"中
    recs = results[ID][:suggestion_num]
    #====
    #最後在result.html中呈現結果
    return render_template("result.html",recs=recs,ID=ID,suggestion_num=suggestion_num,search_comp=search_comp,search_job_title=search_job_title)

#以下對應result.html中"=>若須重新搜尋請點我"的連結，主要是重新搜尋資料時須先將前一次的所有excel與csv資料全部刪除並重新導向首頁 
@app.route('/restart')
def method_name():
    to_be_deleted_csv_files = glob.glob('static/*.csv')
    for file in to_be_deleted_csv_files:
        try:
            os.remove(file)
        except OSError as e:
            print(f"Error:{ e.strerror}")

    to_be_deleted_xlsx_files = glob.glob('static/*.xlsx')
    for file in to_be_deleted_xlsx_files:
        try:
            os.remove(file)
        except OSError as e:
            print(f"Error:{ e.strerror}")

    return redirect("http://127.0.0.1:5000/") #重新導向

#啟動網站伺服器，可透過port參數指定埠號
if __name__=="__main__":
    app.run(port=5000)