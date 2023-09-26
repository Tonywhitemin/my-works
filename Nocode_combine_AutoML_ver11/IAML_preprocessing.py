import os
#from flask import Flask #載入FLASK
from flask import request
from flask import render_template
from flask import redirect
from flask import session
from flask import send_file
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
import shutil
import seaborn as sns #圖表模塊
import zipfile #壓縮檔案模組
from os.path import basename
from flask import Blueprint
import json
from function_login_requirement import login_required

df_pre= Blueprint("df_pre",__name__)#利用Blueprint套件達到整合Flask各子功能.py檔


@df_pre.route('/reset',methods=["POST","GET"]) #220908新增當有錯誤但無法排除時強制回到首頁
@login_required
def reset():
    f_path=session["folder_path"]
    shutil.rmtree(f_path)
    return redirect("/homepage")


@df_pre.route('/df_para_modify',methods=["POST","GET"])
@login_required
def df_para_modify():
    #==訓練資料集讀取==
    fp=session["folder_path"]
    fn=session["filename"]
    df=pd.read_csv(fp+"/"+fn)
    
    

    #＝＝＝＝＝＝＝220826當缺失值有使用特殊代碼時的應變方式＝＝＝＝＝＝＝
    try:
        label_column=request.values["label_column"] #確認label欄位
        session["label_column"]=label_column
        #=====230620 debug for新增若使用者上傳的資料集label中只有單一數字時要跳錯誤=====
        if len(set(df[label_column]))==1:
            #==以下為欄位list==
            features_list=[]
            for i in df.columns:
                features_list.append(i)   
            #====以下這段為修正顯示到前端的欄位屬性為中文====
            features_dtype_list=[]
            for j in df.columns:
                #print(j,"改變前的dtype: ",df[j].dtype)
                if df[j].dtype=="int64":
                    int64_to_int="整數(int)"
                    features_dtype_list.append(int64_to_int)
                elif df[j].dtype=="float64":
                    float64_to_float="浮點數(float)"
                    features_dtype_list.append(float64_to_float)
                elif df[j].dtype=="object":
                    object_to_category="無序類別(Nominal_category)"
                    features_dtype_list.append(object_to_category)
                elif df[j].dtype=="str":
                    object_to_category="字串(str)"
                    features_dtype_list.append(object_to_category)
            return render_template("dataset_current_info_single_label_wrong.html",l1=features_list, j1=features_dtype_list)
        #=====
    except:
        session["label_column"]="尚未選擇標籤欄位"
        pass

    missing_code=request.form.getlist("missing_code") #確認缺失值代碼
    # print(missing_code)
    #=============================
    #221122測試
    # print("缺失值代號取代成空值之前的dtype")
    # for j in df.columns:
    #         print(j,"改變前的dtype: ",df[j].dtype)
    #=============================
    dtype_col=request.form.getlist("dtype") #得到欄位屬性的list
    # print("dtype_col: ",dtype_col)
    #=====221020測試將有序與無率的類別特徵區分開來=====
    numerical_list=[] #數值屬性特徵欄位清單
    numerical_col_property=[] #221122為了讓拆開來的屬性在前端能正確呈現所以新增此空list
    nominal_cata_list=[]#無序特徵欄位清單
    nominal_col_property=[] #221122為了讓拆開來的屬性在前端能正確呈現所以新增此空list
    ordinal_cata_list=[]#有序特徵欄位清單
    ordinal_col_property=[] #221122為了讓拆開來的屬性在前端能正確呈現所以新增此空list
    for index, value in enumerate(dtype_col):
        if value == "整數(int)":
            dtype_col[index] = "int64"
            if df.columns[index]==label_column: #221121 debug for 當標籤欄位存在時不要讓標籤欄位的處理顯示在前端
                pass
            else:
                numerical_list.append(df.columns[index])
                numerical_col_property.append("整數(int)")
        elif value == "浮點數(float)":
            dtype_col[index] = "float64"
            if df.columns[index]==label_column: #221121 debug for 當標籤欄位存在時不要讓標籤欄位的處理顯示在前端
                pass
            else:
                numerical_list.append(df.columns[index])
                numerical_col_property.append("浮點數(float)")

        elif value == "字串(str)":
            dtype_col[index] = "str"
            #221121字串尚未統合進處理當中，先閒置 #TODO
           
        elif value == "無序類別(Nominal_category)":
            dtype_col[index] = "object"
            if df.columns[index]==label_column: #221121 debug for 當標籤欄位存在時不要讓標籤欄位的處理顯示在前端
                pass
            else:
                nominal_cata_list.append(df.columns[index])
                nominal_col_property.append("無序類別(Nominal_category)")

        elif value == "有序類別(Ordinal_category)":
            dtype_col[index] = "object"
            if df.columns[index]==label_column: #221121 debug for 當標籤欄位存在時不要讓標籤欄位的處理顯示在前端
                pass
            else:
                ordinal_cata_list.append(df.columns[index])
                ordinal_col_property.append("有序類別(Ordinal_category)")

    session["numerical_list"]=numerical_list
    session["nominal_cata_list"]=nominal_cata_list
    session["ordinal_cata_list"]=ordinal_cata_list

    #=====220826 dtype先定義，避免因先刪除了欄位導致欄位數量不一致======
    #===220826在此處同步處理測試資料集===
    test_df_folder_path=session["test_df_folder_path"]
    test_df_filename=session["test_df_filename"]
    test_df_filename2=session["test_df_filename2"]
    test_df_filename3=session["test_df_filename3"]
    if os.path.exists(test_df_folder_path+"/"+test_df_filename):
        df_test=pd.read_csv(test_df_folder_path+"/"+test_df_filename)
    if os.path.exists(test_df_folder_path+"/"+test_df_filename2):
        df_test2=pd.read_csv(test_df_folder_path+"/"+test_df_filename2)
    if os.path.exists(test_df_folder_path+"/"+test_df_filename3):
        df_test3=pd.read_csv(test_df_folder_path+"/"+test_df_filename3)
    #===以上為讀取測試資料集===
    #===以下開始做欄位屬性變更===
    train_error_list=[]
    test1_error_list=[]
    test2_error_list=[]
    test3_error_list=[]
    for index_num,col in enumerate(df.columns):    
        #220817加上警告屬性無法轉換的提示
        try:
            df[col]=df[col].astype(dtype_col[index_num])
            
        except ValueError as v: #220831將屬性變更錯誤一次性匯出
            train_error_list.append("Error:訓練資料集的"+df.columns[index_num]+"欄位屬性無法變更為"+dtype_col[index_num])
        continue
    if os.path.exists(test_df_folder_path+"/"+test_df_filename):
        for index_num,col in enumerate(df.columns):
            try:
                df_test[col]=df_test[col].astype(dtype_col[index_num])#220826同步處理測試資料集
            except ValueError as v: #220908將測試資料集的欄位屬性轉換功能新增
                test1_error_list.append("Error:第一份測試資料集的"+df_test.columns[index_num]+"欄位屬性無法變更為"+dtype_col[index_num]+"!")
            continue
        
    if os.path.exists(test_df_folder_path+"/"+test_df_filename2):
        for index_num,col in enumerate(df.columns):
            try:
                df_test2[col]=df_test2[col].astype(dtype_col[index_num])#220906同步處理測試資料集
            except ValueError as v: #220908將測試資料集的欄位屬性轉換功能新增
                test2_error_list.append("Error:第二份測試資料集的"+df_test2.columns[index_num]+"欄位屬性無法變更為"+dtype_col[index_num]+"!")
            continue
    
    if os.path.exists(test_df_folder_path+"/"+test_df_filename3):
        for index_num,col in enumerate(df.columns):
            try:
                df_test3[col]=df_test3[col].astype(dtype_col[index_num])#220906同步處理測試資料集
            except ValueError as v: #220908將測試資料集的欄位屬性轉換功能新增
                test3_error_list.append("Error:第三份測試資料集的"+df_test3.columns[index_num]+"欄位屬性無法變更為"+dtype_col[index_num]+"!")
            continue
    #=====以下為220913當有屬性無法轉換時要重新來過=======
    if  train_error_list!=[] or test1_error_list!=[] or test2_error_list!=[] or test3_error_list!=[]:
        #==訓練資料集讀取==

        fp=session["folder_path"]
        fn=session["filename"]
        df=pd.read_csv(fp+"/"+fn)
        #==以下為欄位list==
        features_list=[]
        for i in df.columns:
            features_list.append(i)   
        #====以下這段為修正顯示到前端的欄位屬性為中文====
        features_dtype_list=[]
        for j in df.columns:
            #print(j,"改變前的dtype: ",df[j].dtype)
            if df[j].dtype=="int64":
                int64_to_int="整數(int)"
                features_dtype_list.append(int64_to_int)
            elif df[j].dtype=="float64":
                float64_to_float="浮點數(float)"
                features_dtype_list.append(float64_to_float)
            elif df[j].dtype=="object":
                object_to_category="無序類別(Nominal_category)"
                features_dtype_list.append(object_to_category)
            elif df[j].dtype=="str":
                object_to_category="字串(str)"
                features_dtype_list.append(object_to_category)
        return render_template("dataset_current_info wrong_property.html",l1=features_list, j1=features_dtype_list,
        train_error_list=train_error_list,test1_error_list=test1_error_list,test2_error_list=test2_error_list,test3_error_list=test3_error_list)
    
    
    #=====220826以下為缺失值代碼取代為空值測試======
    for index, col in enumerate(df.columns):
        #print("df[col].dtype結果為:",df[col].dtype)
        if missing_code[index]!="請輸入代號":
            # print(missing_code[index],"缺失值代號的屬性: ",type(missing_code[index]))
            if df[col].dtype=="int64":
                    df[col]=df[col].replace(int(missing_code[index]),np.nan)
                    if os.path.exists(test_df_folder_path+"/"+test_df_filename):
                        df_test[col]=df_test[col].replace(int(missing_code[index]),np.nan) #220826同步處理測試資料集
                    if os.path.exists(test_df_folder_path+"/"+test_df_filename2):
                        df_test2[col]=df_test2[col].replace(int(missing_code[index]),np.nan)#220906同步處理測試資料集
                    if os.path.exists(test_df_folder_path+"/"+test_df_filename3):
                        df_test3[col]=df_test3[col].replace(int(missing_code[index]),np.nan)#220906同步處理測試資料集
            elif df[col].dtype=="float64":
                    df[col]=df[col].replace(int(missing_code[index]),np.nan)
                    if os.path.exists(test_df_folder_path+"/"+test_df_filename):
                        df_test[col]=df_test[col].replace(int(missing_code[index]),np.nan) #220826同步處理測試資料集
                    if os.path.exists(test_df_folder_path+"/"+test_df_filename2):
                        df_test2[col]=df_test2[col].replace(int(missing_code[index]),np.nan)#220906同步處理測試資料集
                    if os.path.exists(test_df_folder_path+"/"+test_df_filename3):
                         df_test3[col]=df_test3[col].replace(int(missing_code[index]),np.nan)#220906同步處理測試資料集
            elif df[col].dtype=="object":
                    # df[col]=df[col].replace(str(missing_code[index]),np.nan)
                    df[col]=df[col].replace(str(missing_code[index]),np.nan)
                    if os.path.exists(test_df_folder_path+"/"+test_df_filename):
                        df_test[col]=df_test[col].replace(str(missing_code[index]),np.nan) #220826同步處理測試資料集
                    if os.path.exists(test_df_folder_path+"/"+test_df_filename2):
                        df_test2[col]=df_test2[col].replace(str(missing_code[index]),np.nan)#220906同步處理測試資料集
                    if os.path.exists(test_df_folder_path+"/"+test_df_filename3):
                         df_test3[col]=df_test3[col].replace(str(missing_code[index]),np.nan)#220906同步處理測試資料集
    #將缺失值代碼轉為空值後先存檔
    df.to_csv(fp+"/"+fn,index=False)
    if os.path.exists(test_df_folder_path+"/"+test_df_filename):
        df_test.to_csv(test_df_folder_path+"/"+test_df_filename,index=False)
    if os.path.exists(test_df_folder_path+"/"+test_df_filename2):
        df_test2.to_csv(test_df_folder_path+"/"+test_df_filename2,index=False)
    if os.path.exists(test_df_folder_path+"/"+test_df_filename3):
        df_test3.to_csv(test_df_folder_path+"/"+test_df_filename3,index=False)
    
    #221121要先將最後確定的欄位屬性存起來方便後面使用
    session["dtype_col"]=dtype_col

    #=======================================================================221121以下開始整合逐欄前處理項目的前端處理=======================================================================
    
    #221121先將資料集拆成數值；有序類別與無序類別
    numerical_list=session["numerical_list"]
    nominal_cata_list=session["nominal_cata_list"]
    ordinal_cata_list=session["ordinal_cata_list"]

    df_numerical=pd.DataFrame(df[numerical_list])
    df_ordinal=pd.DataFrame(df[ordinal_cata_list])
    df_nominal=pd.DataFrame(df[nominal_cata_list])

    
    
    #===============================================

    #=以下為欄位list==
    df_numerical_features_list=[] #數值型欄位清單
    for i in df_numerical.columns:
       df_numerical_features_list.append(i)

    df_ordinal_features_list=[] #有序類別型欄位清單
    for i in df_ordinal.columns:
       df_ordinal_features_list.append(i)
    
    df_nominal_features_list=[] #無序類別型欄位清單
    for i in df_nominal.columns:
       df_nominal_features_list.append(i)
    #=====以下為欄位屬性呈現到前端用===== #221122發現這裡的欄位呈現可能會跟一開始使用者所選的內容不同所以暫時先隱藏起來
    # property_of_df_numerical=[]
    # property_of_df_ordinal=[]
    # property_of_df_nominal=[]
    # for p in df_numerical.columns:
    #     if df_numerical[p].dtype=="int64":
    #         property_of_df_numerical.append("整數(int)")
    #     if df_numerical[p].dtype=="float64":
    #         property_of_df_numerical.append("浮點數(float)")

    # for p in df_ordinal.columns:
    #     property_of_df_ordinal.append("有序類別(ordinal)")
    
    # for p in df_nominal.columns:
    #     property_of_df_nominal.append("無序類別(nominal)")
    #=====以下為顯示現有欄位資料與缺失率====
    #數值型欄位缺失
    df_numerical_missing=df_numerical.isnull().sum(axis=0)/df_numerical.shape[0]*100
    df_numerical_missing=pd.DataFrame(df_numerical_missing)

    df_numerical_missing["column_name"]=df_numerical_missing.index
    df_numerical_missing_rate=[]
    for i in range(len(df_numerical_missing["column_name"])):
        df_numerical_missing_rate.append(round(df_numerical_missing.iloc[i,0],2))
    
    # print("df_numerical_missing_rate: ",df_numerical_missing_rate)
    
    #有序型類別欄位缺失
    df_ordinal_missing=df_ordinal.isnull().sum(axis=0)/df_ordinal.shape[0]*100
    df_ordinal_missing=pd.DataFrame(df_ordinal_missing)

    df_ordinal_missing["column_name"]=df_ordinal_missing.index
    df_ordinal_missing_rate=[]
    for i in range(len(df_ordinal_missing["column_name"])):
        df_ordinal_missing_rate.append(round(df_ordinal_missing.iloc[i,0],2))
    
    #無序型類別欄位缺失
    df_nominal_missing=df_nominal.isnull().sum(axis=0)/df_nominal.shape[0]*100
    df_nominal_missing=pd.DataFrame(df_nominal_missing)

    df_nominal_missing["column_name"]=df_nominal_missing.index
    df_nominal_missing_rate=[]
    for i in range(len(df_nominal_missing["column_name"])):
       df_nominal_missing_rate.append(round(df_nominal_missing.iloc[i,0],2))

    #======221024以下這段是要將"有"序特徵欄位的細項輸出到前端用(若前端使用者希望有序特徵使用label encoding時須顯示出)=====
    ordinal_df=pd.DataFrame(df_ordinal)
    ordinal_col=[]#將欄位名稱丟入這裡
    ordinal_option=[]#將欄位內選項清單丟入這裡
    for i in ordinal_df.columns:
        ordinal_col.append(i)
        ordinal_all_option=list(set(ordinal_df[i]))#用set將不重複的選項列成list
        for a in ordinal_all_option:
            if str(a)!="nan": #221103 debug for 若一開始資料集中類別屬性變數有缺失值時，前端若要指定label encoding代號時會出現"nan"要使用者編輯代號
                # print(type(a))
                ordinal_option.append(a)#將選項加入
                # print("ordinal_option:\n",ordinal_option)
        #以下這段目的為欄位與選項數量一定不一致，考量後續在前端迴圈要製作表格，所以會比較當欄位數量比選項少時，自動增加同欄位名稱到與選項數量一致    
        for l in range(0,len(ordinal_option)):
            if len(ordinal_col)<len(ordinal_option):
                ordinal_col.append(i)
    # session["ordinal_option"]=ordinal_option #221025為了後面mapping用

    #=====221110以下這段是為了讓使用者若選擇dropna以後部分選項要disable用=====
    numericalidname=[] #若使用者選dropna則把填補值選項在前端disable掉
    numerical_disableid=[] #for 填補值欄位id 要disable用
    numerical_drop_col_then_disable=[] #221115若欄位句選刪除時後面選項都disable掉
    numerical_drop_col_then_disable_outlier=[]
    numerical_drop_col_then_disable_normalization=[]
    for i in range(len(df_numerical_features_list)):
        numericalidname.append("numericalid"+str(i))
        numerical_disableid.append("numerical_disableid"+str(i))
        numerical_drop_col_then_disable.append("numerical_drop_col_disable_"+str(i))
        numerical_drop_col_then_disable_outlier.append("disable_outlier_"+str(i))
        numerical_drop_col_then_disable_normalization.append("disable_normalization_"+str(i))

    ordinalidname=[] #若使用者選dropna則把填補值選項在前端disable掉
    ordinal_disableid=[] #for 填補值欄位id 要disable用
    ordinal_drop_col_then_disable=[] #221115若欄位句選刪除時後面選項都disable掉
    ord_handle=[]
    for i in range(len(df_ordinal_features_list)):
        ordinalidname.append("ordinalid"+str(i))
        ordinal_disableid.append("ordinal_disableid"+str(i))
        ordinal_drop_col_then_disable.append("ordinal_drop_col_disable_"+str(i))
        ord_handle.append("ord_handle_"+str(i))

    nominalidname=[] #若使用者選dropna則把填補值選項在前端disable掉
    nominal_disableid=[] #for 填補值欄位id 要disable用
    nominal_drop_col_then_disable=[] #221115若欄位句選刪除時後面選項都disable掉
    for i in range(len(df_nominal_features_list)):
        nominalidname.append("nominalid"+str(i))
        nominal_disableid.append("nominal_disableid"+str(i))
        nominal_drop_col_then_disable.append("nominal_drop_col_disable_"+str(i))

    return render_template("dataset_preprocessing.html",
        df_numerical_features_list=df_numerical_features_list,df_ordinal_features_list=df_ordinal_features_list,df_nominal_features_list=df_nominal_features_list, #回饋欄位
        property_of_df_numerical=numerical_col_property ,property_of_df_ordinal=ordinal_col_property , property_of_df_nominal=nominal_col_property, #回饋欄位屬性
        ordinal_col=ordinal_col,ordinal_option=ordinal_option, #221024此行是將有序無序欄位細項輸出但看使用者要不要選用
        df_numerical_missing_rate=df_numerical_missing_rate, df_ordinal_missing_rate=df_ordinal_missing_rate,df_nominal_missing_rate=df_nominal_missing_rate, #回饋缺失率
        numericalidname=numericalidname,ordinalidname=ordinalidname,nominalidname=nominalidname, #221110為了讓使用者若選擇dropna以後部分選項要disable用
        numerical_disableid=numerical_disableid, ordinal_disableid=ordinal_disableid, nominal_disableid=nominal_disableid, #221110為了讓使用者若選擇dropna以後部分選項要disable用
        numerical_drop_col_then_disable=numerical_drop_col_then_disable,ordinal_drop_col_then_disable=ordinal_drop_col_then_disable,nominal_drop_col_then_disable=nominal_drop_col_then_disable, #221115若欄位句選刪除時後面選項都disable掉
        numerical_drop_col_then_disable_outlier=numerical_drop_col_then_disable_outlier,numerical_drop_col_then_disable_normalization=numerical_drop_col_then_disable_normalization, #221115為解決不同欄位相同class會有toggle衝突問題所以分別給class name
        ord_handle=ord_handle, #221115給有序類別encoding處理方式的清單給個id
        ) 





@df_pre.route('/handle_preprocessing',methods=["POST","GET"])
@login_required
def handle_preprocessing():
        
    #讀取訓練資料集
    fp=session["folder_path"]
    fn=session["filename"]
    df=pd.read_csv(fp+"/"+fn)

    
    numerical_list=session["numerical_list"]
    nominal_cata_list=session["nominal_cata_list"]
    ordinal_cata_list=session["ordinal_cata_list"]

    df_numerical=pd.DataFrame(df[numerical_list])
    df_ordinal=pd.DataFrame(df[ordinal_cata_list])
    df_nominal=pd.DataFrame(df[nominal_cata_list])
    
    #================================================================221121整合成逐欄處理前處理資料=====================================================================
    #======221111以下開始接收前端資料======
    original_df_columns=list(df.columns)
    final_column=[] #目的為確認總清單中若有欄位減少則要先drop欄位
    numerical_drop_col=[] #221115為了後面拆三個df使用，在最後整並上可以簡化一點
    ordinal_drop_col=[]
    nominal_drop_col=[]
   
    numerical_undrop_columns=request.form.getlist("numerical_drop_col") #得到數值型欄位最後留下的欄位清單
    ordinal_undrop_columns=request.form.getlist("ordinal_drop_col") #得到有序型欄位最後留下的欄位清單
    nominal_undrop_columns=request.form.getlist("nominal_drop_col") #得到無序型欄位最後留下的欄位清單
    for i,ans in enumerate(numerical_undrop_columns):
        if ans=="no":
            final_column.append(df_numerical.columns[i])
        elif ans=="yes":
           numerical_drop_col.append(df_numerical.columns[i])
           
    df_numerical=df_numerical.drop(numerical_drop_col,axis=1)

    for i,ans in enumerate(ordinal_undrop_columns):
        if ans=="no":
            final_column.append(df_ordinal.columns[i])
        elif ans=="yes":
            ordinal_drop_col.append(df_ordinal.columns[i])   

    df_ordinal=df_ordinal.drop(ordinal_drop_col,axis=1)

    for i,ans in enumerate(nominal_undrop_columns):
        if ans=="no":    
            final_column.append(df_nominal.columns[i])
        elif ans=="yes":
            nominal_drop_col.append(df_nominal.columns[i])
            
    df_nominal=df_nominal.drop(nominal_drop_col,axis=1)

    label_column=session["label_column"]
    if label_column!="尚未選擇標籤欄位":
        final_column.append(label_column) #221121若存在標籤欄位則此處要先加入標籤欄位，避免標籤欄位被drop掉
    
    #以下這段是當final_column數量比原始欄位數少的時候要將
    if len(final_column)<len(original_df_columns):
        drop_col_index=[] #將drop column的index放進這裡以便後面刪除欄位屬性時要將對應的值刪除掉
        for i,col_name in enumerate(df.columns):
            if col_name in list(set(original_df_columns).difference(set(final_column))):
                # print("該欄位所屬的index為：",i)
                drop_col_index.append(i)
        df=df.drop(list(set(original_df_columns).difference(set(final_column))),axis=1)
        final_drop_columns=list(set(original_df_columns).difference(set(final_column))) #221212新增此項目以便加入最後輸出的json檔中
        # print("drop欄位以後的df:\n",df)
        # print("差異欄位：",list(set(original_df_columns).difference(set(final_column))))
        session["drop_col_index"]=drop_col_index
    else:
        session["drop_col_index"]=[]
        final_drop_columns=[] #221226 debug for 如果沒有給空list到後面json檔時會出錯
    

    
    #=====221111下面這段是處理數值類型變數outlier=====
    numerical_outlier=request.form.getlist("numerical_outlier")
    outlier_UL_list=[] #221129新增以便讓測試資料集可使用
    outlier_LL_list=[] #221129新增以便讓測試資料集可使用
    for i, ans in enumerate(numerical_outlier):
        if ans=="yes":
            # print("df_numerical[df_numerical.columns[i]]",df_numerical[df_numerical.columns[i]]) #取出會執行outlier的欄位
            Q1,Q3=np.nanpercentile(df_numerical[df_numerical.columns[i]],[25,75])
            IQR=Q3-Q1
            UL=Q3+1.5*IQR
            outlier_UL_list.append(UL) #221129將outlier上限值加入list
            LL=Q1-1.5*IQR
            outlier_LL_list.append(LL) #221129將outlier下限值加入list
            outliers_values=df_numerical[df_numerical.columns[i]][(df_numerical[df_numerical.columns[i]]>UL)|(df_numerical[df_numerical.columns[i]]<LL)]
            # print("outliers_values:",outliers_values)
            
            df_numerical[df_numerical.columns[i]]=df_numerical[df_numerical.columns[i]].replace([outliers_values],np.nan)
            df[df_numerical.columns[i]]=df_numerical[df_numerical.columns[i]]
    # print("df_numerical:\n",df_numerical)
    
    #=====221111以下開始處理dropna部份=====
    need_dropna_column=[] #目的為確認總清單中若有欄位要執行dropna
    numerical_dropna=request.form.getlist("numerical_dropna") #得到數值型欄位哪些要執行dropna
    
    ordinal_dropna=request.form.getlist("ordinal_dropna") #得到有序型欄位哪些要執行dropna
    
    nominal_dropna=request.form.getlist("nominal_dropna") #得到無序型欄位哪些要執行dropna
    

    for i, ans in enumerate(numerical_dropna):
        if ans=="yes":
            need_dropna_column.append(df_numerical.columns[i])

    for i, ans in enumerate(ordinal_dropna):
        if ans=="yes":
            need_dropna_column.append(df_ordinal.columns[i])

    for i, ans in enumerate(nominal_dropna):
        if ans=="yes":
            need_dropna_column.append(df_nominal.columns[i])

    # print("need_dropna_column:",need_dropna_column)
    # print("dropna以前的df:\n",df)
    df=df.dropna(subset=need_dropna_column) #subset用法是只選擇要dropna的欄位做處理就好其餘不動
    df=df.reset_index(drop=True) #221103要將被dropna的index重設後面才不會有錯
    # print("剛dropna後的df:\n",df)
    
    #=====221114若有標籤欄位必須在處理完drop欄位與dropna以後將標籤欄位獨立出來避免資料筆數異常===== 
    label_column=session["label_column"]
    
    if label_column!='尚未選擇標籤欄位':
        df_label=df[label_column] 
        
        df=df.drop(label_column,axis=1)
        
    
    #=====221114開始處理缺失值填補=====
    #=====以下這段目的是要再將做完上述前處理的各類型特徵再拆出，記得到時候與主程式連接時要轉為依使用者選擇欄位屬性定義 
    df_numerical=pd.DataFrame(df[df_numerical.columns])
    df_ordinal=pd.DataFrame(df[df_ordinal.columns])
    df_nominal=pd.DataFrame(df[df_nominal.columns])
    
    #221114以下為數值型補值
    numerical_fillna=request.form.getlist("numerical_fill_na") #得到數值型欄位fillna方法清單
    # print("修正前的numerical_fillna： ",numerical_fillna)

    #=====221123 debug for 若前端使用者選了dropna以後因填補值會被disable導致上面清單抓取資料時會有錯位的問題=====
    if_dropna_disable_then_expand_numerical_fillna=["median"]*len(numerical_dropna) #221123先建立一個等長度的list然後填入預設值
    # ordinal_dropna
    # nominal_dropna
    dummy_num=0 #讓實際上的使用者所選值帶入用的index
    for i, ans in enumerate(numerical_dropna):
        if ans=="no":
            if_dropna_disable_then_expand_numerical_fillna[i]=numerical_fillna[dummy_num]
            dummy_num+=1
    numerical_fillna=if_dropna_disable_then_expand_numerical_fillna
    # print("修正後的numerical_fillna： ",numerical_fillna)
    #=====

    # print("numerical_fillna清單：",numerical_fillna)
    fillna_with_mean_list=[]
    fillna_with_median_list=[]
    for i, method in enumerate(numerical_fillna):
        if method=="mean":
            fillna_with_mean_list.append(df_numerical.columns[i])
        elif method=="median":
            fillna_with_median_list.append(df_numerical.columns[i])
    numerical_imputer_mean = SimpleImputer(strategy="mean")  #預設參數strategy="mean" , 可改為 "median"
    numerical_imputer_median = SimpleImputer(strategy="median")  #預設參數strategy="mean" , 可改為 "median"
    
    if fillna_with_mean_list!=[]:
        # print("原始df_numerical:\n",df_numerical.head())
        numerical_imputer_mean.fit(df_numerical[fillna_with_mean_list]) #這邊先用fit是為了後面測試資料集用
        df_numerical[fillna_with_mean_list]= numerical_imputer_mean.transform(df_numerical[fillna_with_mean_list]) 
        #=====221114以下這段是為了取出補值的內容以便後面紀錄參數用=====
        # print("get_feature_names_out:",numerical_imputer_mean.get_feature_names_out()) #這行是取得對應的特徵欄位
        dummy_dict_for_mean_Imputer={} #建立一個空字典以便建立一個dummy資料集讓缺失值填入
        for i in range(len(fillna_with_mean_list)):
            dummy_dict_for_mean_Imputer.update({fillna_with_mean_list[i]:[np.nan,1]}) #建立一個只有2列的資料，其中第1列為空值讓imputer填入
        # print("dummy_dict_for_mean_Imputer:\n",dummy_dict_for_mean_Imputer) #確認效果用
        mean_transform_dummy=pd.DataFrame(dummy_dict_for_mean_Imputer) #將字典轉換為dataframe
        imputer_mean_list=numerical_imputer_mean.transform(mean_transform_dummy)[0] #將轉換值取出(為list型態)
        # print("numerical_imputer_transform結果:",numerical_imputer_mean.transform(df_transform_dummy)[0]) #將轉換值取出
        # print("補值後df_numerical:\n",df_numerical.head())
        #========================================================
    else:
        imputer_mean_list=[] #221130 為了後面json輸出各參數紀錄時使用

    if fillna_with_median_list!=[]:
        numerical_imputer_median.fit(df_numerical[fillna_with_median_list])
        df_numerical[fillna_with_median_list]= numerical_imputer_median.transform(df_numerical[fillna_with_median_list])
        #=====221114以下這段是為了取出補值的內容以便後面存檔用=====
        dummy_dict_for_median_Imputer={} #建立一個空字典以便建立一個dummy資料集讓缺失值填入
        for i in range(len(fillna_with_median_list)):
            dummy_dict_for_median_Imputer.update({fillna_with_median_list[i]:[np.nan,1]}) #建立一個只有2列的資料，其中第1列為空值讓imputer填入
        # print("dummy_dict_for_median_Imputer:",dummy_dict_for_median_Imputer)
        median_transform_dummy=pd.DataFrame(dummy_dict_for_median_Imputer) #將字典轉換為dataframe
        imputer_median_list=numerical_imputer_median.transform(median_transform_dummy)[0] #將轉換值取出(為list型態)
    else:
         imputer_median_list=[] #221130 為了後面json輸出各參數紀錄時使用
        #========================================================
    # print("df_numerical:\n",df_numerical)
    #221114以下為有序類別型補值
    ordinal_fillna=request.form.getlist("ordinal_fill_na") #得到有序型欄位fillna方法清單
    #=====221123 debug for 若前端使用者選了dropna以後因填補值會被disable導致上面清單抓取資料時會有錯位的問題=====
    if_dropna_disable_then_expand_ordinal_fillna=["mode"]*len(ordinal_dropna) #221123先建立一個等長度的list然後填入預設值
    # nominal_dropna
    dummy_num_ord=0 #讓實際上的使用者所選值帶入用的index
    for i, ans in enumerate(ordinal_dropna):
        if ans=="no":
            if_dropna_disable_then_expand_ordinal_fillna[i]=ordinal_fillna[dummy_num_ord]
            dummy_num_ord+=1
    ordinal_fillna=if_dropna_disable_then_expand_ordinal_fillna
    # print("修正後的ordinal_fillna： ",ordinal_fillna)
    #=====
    ord_fillna_with_mode_list=[]
    ord_fillna_with_unknown_list=[]
    for i, method in enumerate(ordinal_fillna):
        if method=="mode":
            ord_fillna_with_mode_list.append(df_ordinal.columns[i])
        elif method=="unknown":
            ord_fillna_with_unknown_list.append(df_ordinal.columns[i])
    ord_mode_list=[] #先把眾數清單個別加入此list中後面測試資料集才不會出錯
    if ord_fillna_with_mode_list!=[]:
        for i in ord_fillna_with_mode_list:
            df_ordinal[i]=df_ordinal[i].fillna(df_ordinal[i].mode()[0])
            ord_mode_list.append(df_ordinal[i].mode()[0]) #眾數的值
    if ord_fillna_with_unknown_list!=[]:
        for i in ord_fillna_with_unknown_list:
            df_ordinal[i]=df_ordinal[i].fillna("Unknown")
    #221114以下為無序類別型補值
    nominal_fillna=request.form.getlist("nominal_fill_na") #得到無序型欄位fillna方法清單

    #=====221123 debug for 若前端使用者選了dropna以後因填補值會被disable導致上面清單抓取資料時會有錯位的問題=====
    if_dropna_disable_then_expand_nominal_fillna=["mode"]*len(nominal_dropna) #221123先建立一個等長度的list然後填入預設值
    dummy_num_nom=0 #讓實際上的使用者所選值帶入用的index
    for i, ans in enumerate(nominal_dropna):
        if ans=="no":
            if_dropna_disable_then_expand_nominal_fillna[i]=nominal_fillna[dummy_num_nom]
            dummy_num_nom+=1
    nominal_fillna=if_dropna_disable_then_expand_nominal_fillna
    # print("修正後的nominal_fillna： ",nominal_fillna)
    #=====
    
    nom_fillna_with_mode_list=[]
    nom_fillna_with_unknown_list=[]
    for i, method in enumerate(nominal_fillna):
        if method=="mode":
            nom_fillna_with_mode_list.append(df_nominal.columns[i])
        elif method=="unknown":
            nom_fillna_with_unknown_list.append(df_nominal.columns[i])
    nom_mode_list=[] #先把眾數清單個別加入此list中後面測試資料集才不會出錯
    if nom_fillna_with_mode_list!=[]:
        for i in nom_fillna_with_mode_list:
            df_nominal[i]=df_nominal[i].fillna(df_nominal[i].mode()[0])
            nom_mode_list.append(df_nominal[i].mode()[0])
    if nom_fillna_with_unknown_list!=[]:
        for i in nom_fillna_with_unknown_list:
           df_nominal[i]=df_nominal[i].fillna("Unknown")
    # print("nom_fillna_with_mode_list:",nom_fillna_with_mode_list)
    # print("nom_fillna_with_unknown_list:",nom_fillna_with_unknown_list)
    # print("df_ordinal:\n",df_ordinal.head())
    # print("df_nominal:\n",df_nominal.head())
    
    #===================221116開始處理標準化的流程=================
    normalization=request.form.getlist("numerical_normalization") #得到numerical_normalization清單
   
    min_max_col=[]
    standard_col=[]
    none_col=[]
    for i,option in enumerate(normalization):
        if option=="min_max":
            min_max_col.append(df_numerical.columns[i])
        elif option=="StandardScaler":
            standard_col.append(df_numerical.columns[i])
        else:
            none_col.append(df_numerical.columns[i])

    if min_max_col!=[]:
        min_Max_scaler = preprocessing.MinMaxScaler()
        min_max=min_Max_scaler.fit(df_numerical[min_max_col])
        df_numerical[min_max_col]=min_max.transform(df_numerical[min_max_col])

    if standard_col!=[]:
        standard_scaler = preprocessing.StandardScaler()
        standard=standard_scaler.fit(df_numerical[standard_col])
        df_numerical[standard_col]=standard.transform(df_numerical[standard_col])
    # print("df_numerical:\n",df_numerical.head())

    #===以下這段是先將one-hot encoding與label encoding前的資料夾先另存以便讓後面的結果解讀可以順利讀出，不然會全部變成數字欄位。注意要與原先標籤欄位拆開的兩個表格合併===
           
    if label_column!='尚未選擇標籤欄位':
        df_before_encoding=pd.concat([df_numerical,df_ordinal,df_nominal,df_label],axis=1)#此處要整併標籤欄位的df
    else:
        df_before_encoding=pd.concat([df_numerical,df_ordinal,df_nominal],axis=1) 
    df_before_encoding.to_csv(fp+"/"+fn[0:-4]+"_before_encoding.csv",index=False)#將尚未執行encoding的資料集先存檔
    #===================================================
    
    #====221116以下是無序資料直接做one-hot處理====
    
    oh=preprocessing.OneHotEncoder() #使用one-hot encoding
    #順向one-hot
    oh.fit(df_nominal) #此處用fit目的為後面要為測試資料集使用
    df_nominal=pd.DataFrame(oh.transform(df_nominal).toarray(),columns=oh.get_feature_names_out())#oh.get_feature_names_out()直接將column原本為數字編碼直接變成正確名稱
    # print("one-hot後的df_nominal:\n",df_nominal.head())

    #=========================================
    #========================221117開始處理有序類別label encoding and one-hot encoding=========================================
    ordinal_encoding=request.form.getlist("ordinal_translate") #得到有序類別變數要用何種方法做encoding清單
    self_define_label_encoding_col=[]
    auto_label_encoding_col=[]
    one_hot_col=[]

    for i, option in enumerate(ordinal_encoding):
        if option=="#tab_1": #對應自定義變數的label_encoding
            self_define_label_encoding_col.append(df_ordinal.columns[i])
        elif option=="#tab_2": #對應default的label_encoding
            auto_label_encoding_col.append(df_ordinal.columns[i])
        elif option=="#tab_3": #對應有序類別但使用者指定用one-hot
            one_hot_col.append(df_ordinal.columns[i])
    
    #=====221117以下這段是自定義label_encoding=====
    if self_define_label_encoding_col!=[]:
        set_new_ordinal_label_code=request.form.getlist("set_new_ordinal_label_code") #得到自定義代碼清單
        #=====221117 debug for 若有欄位不是使用自定義時會有欄位對應值抓錯問題=====
        # print("原始set_new_ordinal_label_code:",set_new_ordinal_label_code)
        self_define_col_len=len(set_new_ordinal_label_code)
        for i in range(self_define_col_len):
            if "123" in set_new_ordinal_label_code:
                set_new_ordinal_label_code.remove("123")
        # print("刪掉預設數值123後的set_new_ordinal_label_code:",set_new_ordinal_label_code)
        #=================================================================
        # print("set_new_ordinal_label_code:",set_new_ordinal_label_code)
        df_ord_self_define_label_encoding=pd.DataFrame(df_ordinal[self_define_label_encoding_col])
        #ordinal_option=session["ordinal_option"] #後面mapping用
        self_define_for_final_json=[] #221024發現用list方式可讓json格式回歸正確輸出
        columnMap={} #此處columnMap要陸續填入選項與轉換的代號值以供後面mapping用

        #221118 debug for 當有一個欄位以上選擇自定義標籤時可能json檔紀錄會有錯序的問題        
        j=-1 #此處j主要目的是填入columnMap中的values,然後因為一開始就會有j+1讓index從0開始所以此處要設定為-1
        k=-1 #此處k主要目的是填入dummy_disc中的values,然後因為一開始就會有k+1讓index從0開始所以此處要設定為-1

        for c in df_ord_self_define_label_encoding.columns:                
            all_option=list(set(df_ord_self_define_label_encoding[c]))#用set將不重複的選項列成list
            print("all_option:",all_option)
            
            for i in range(len(all_option)):
                j+=1
                columnMap.update({all_option[i]:set_new_ordinal_label_code[j]})
                

            dummy_disc={} #寫入json檔的coding欄位用
            
            self_define_for_json={
                        "column_name":c,
                        "coding":dummy_disc
                    }

            for i,a in enumerate(all_option): #取出單一欄位中若有多選項則逐一取出
                k+=1
                dummy_disc.update({a:int(set_new_ordinal_label_code[k])}) #key為選項，value為自定義的值
                    

            self_define_for_final_json.append(self_define_for_json) #將正確格式加入原先的list中（注意是用append）
            df_ord_self_define_label_encoding[c] = df_ord_self_define_label_encoding[c].map(columnMap) #開始抽換掉原先資料集中的選項
            # print("df_ord_self_define_label_encoding:",df_ord_self_define_label_encoding)
            # print(for_final_json)
            
        # print("columnMap: ",columnMap)
        # print("dummy_disc:",dummy_disc)
        
        with open(fp+"/"+"ordinal_self_define_code.json", "w",encoding="utf-8") as f: #注意要用encoding="utf-8"以及下面的ensure_ascii=False才可寫入中文
            json.dump(self_define_for_final_json, f, indent = 2,ensure_ascii=False) #寫入json檔
    else:
        self_define_for_final_json=[] #221130為了後面json輸出前處理參數用

    #=====221117以下這段是default label_encoding=====
    if auto_label_encoding_col!=[]:
        df_ord_auto_label_encoding=pd.DataFrame(df_ordinal[auto_label_encoding_col])
        labelencoder = LabelEncoder()
        # df_ordinal=df[ordinal_cata_list] #將無序欄位拆出原本資料集（注意：此處df不包含label欄位）
        # df_others=df.drop(ordinal_cata_list,axis=1) #將其餘欄位獨立出
        auto_label_encoding_for_final_json=[] #221024發現用list方式可讓json格式回歸正確輸出
        for c in df_ord_auto_label_encoding.columns:
            labelencoder.fit(df_ord_auto_label_encoding[c])
            df_ord_auto_label_encoding[c]= labelencoder.transform(df_ord_auto_label_encoding[c])
            # print(labelencoder.classes_)#print出該欄位的對應編碼
            labelencoder_name_mapping = dict(zip(labelencoder.classes_, labelencoder.transform(labelencoder.classes_)))#將該欄位的對應編碼轉變成字典結構
            
            auto_label_encoding_for_json={
                        "column_name":c,
                        "coding":labelencoder_name_mapping
                    }

            auto_label_encoding_for_final_json.append(auto_label_encoding_for_json) #將正確格式加入原先的list中（注意是用append）
            # print(for_final_json)
            

        # print("for_final_json",for_final_json)

        #下面class語法參考網址：https://stackoverflow.com/questions/50916422/python-typeerror-object-of-type-int64-is-not-json-serializable
        #原因：因為上面的labelencoder_name_mapping在輸出到json dump時會因為value的屬性問題導致無法寫入故需要下面的class做屬性轉換
        class NpEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                if isinstance(obj, np.floating):
                    return float(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                return super(NpEncoder, self).default(obj)

     

        with open(fp+"/"+"ordinal_default_code.json", "w",encoding="utf-8") as f: #注意要用encoding="utf-8"以及下面的ensure_ascii=False才可寫入中文
            json.dump(auto_label_encoding_for_final_json, f,cls=NpEncoder ,indent = 2,ensure_ascii=False) #寫入json檔，注意這邊要套用cls=NpEncoder語法
    else:
        auto_label_encoding_for_final_json=[] #221130為了後面json輸出前處理參數用
        
    #=====221117以下這段是使用者選擇有序類別欄位做one-hot encoding=====
    if one_hot_col!=[]:
        df_ord_one_hot=pd.DataFrame(df_ordinal[one_hot_col])
        ordinal_oh=preprocessing.OneHotEncoder() #使用one-hot encoding
        #順向one-hot
        ordinal_oh.fit(df_ord_one_hot) #此處用fit目的為後面要為測試資料集使用
        df_ord_one_hot=pd.DataFrame(ordinal_oh.transform(df_ord_one_hot).toarray(),columns=ordinal_oh.get_feature_names_out())#oh.get_feature_names_out()直接將column原本為數字編碼直接變成正確名稱
        # print("有序類別特徵經過df_ord_one_hot:\n",df_ord_one_hot)

    #221117將df_ordinal從上面三個情況下整並起來
    if self_define_label_encoding_col!=[] and auto_label_encoding_col!=[] and one_hot_col!=[]: #當有序類別同時存在三種處理方法時（label encoding自定義/label encoding default/one-hot)
        df_ordinal=pd.concat([df_ord_self_define_label_encoding, df_ord_auto_label_encoding,df_ord_one_hot],axis=1)
    
    elif self_define_label_encoding_col!=[] and auto_label_encoding_col!=[] and one_hot_col==[]:#當有序類別同時存在兩種處理方法時（label encoding自定義/label encoding default)
        df_ordinal=pd.concat([df_ord_self_define_label_encoding, df_ord_auto_label_encoding],axis=1)
    
    elif self_define_label_encoding_col!=[] and auto_label_encoding_col==[] and one_hot_col!=[]:#當有序類別同時存在兩種處理方法時（label encoding自定義/one-hot)
        df_ordinal=pd.concat([df_ord_self_define_label_encoding, df_ord_one_hot],axis=1)
    
    elif self_define_label_encoding_col==[] and auto_label_encoding_col!=[] and one_hot_col!=[]:#當有序類別同時存在兩種處理方法時（label encoding default/one-hot)
        df_ordinal=pd.concat([df_ord_auto_label_encoding, df_ord_one_hot],axis=1)
    
    #221118 debug for 忘記可能會有僅出現一種選項的情況所以加上以下三段...

    elif self_define_label_encoding_col!=[] and auto_label_encoding_col==[] and one_hot_col==[]: #當有序類別僅存在一種處理方法時（label encoding自定義)
        df_ordinal=df_ord_self_define_label_encoding
    
    elif self_define_label_encoding_col==[] and auto_label_encoding_col!=[] and one_hot_col==[]: #當有序類別僅存在一種處理方法時（label encoding default)
        df_ordinal=df_ord_auto_label_encoding

    elif self_define_label_encoding_col==[] and auto_label_encoding_col==[] and one_hot_col!=[]: #當有序類別僅存在一種處理方法時（one-hot)
        df_ordinal=df_ord_one_hot

    # df_ordinal.to_csv("df_ordinal_after_preprocessing.csv",index=False)
    
    #=====221121 將前處理完後的各屬性資料欄位整併=====
    #=====221121整合時記得加上label欄位有無的判定===== 
    label_column_check= session["label_column"]
    if label_column_check!="尚未選擇標籤欄位": #有標籤欄位存在的前提
        df=pd.concat([df_numerical,df_ordinal,df_nominal,df_label],axis=1)
        df.to_csv(fp+"/"+fn[0:-4]+"_after_preprocessing.csv",index=False)
    else: #沒有標籤欄位的前提
        df=pd.concat([df_numerical,df_ordinal,df_nominal],axis=1)
        df.to_csv(fp+"/"+fn[0:-4]+"_after_preprocessing.csv",index=False)
    #===================================================================================
#221122測試資料集導入函式
    def test_df_preprocessing(insert_test_df):
        
        #==========以下拆分不同屬性特徵===========
        test_df_numerical=pd.DataFrame(insert_test_df[numerical_list])
        test_df_ordinal=pd.DataFrame(insert_test_df[ordinal_cata_list])
        test_df_nominal=pd.DataFrame(insert_test_df[nominal_cata_list])
        #=====以下為使用者指定刪除欄位使用=====
        test_df_numerical=test_df_numerical.drop(numerical_drop_col,axis=1)
        test_df_ordinal=test_df_ordinal.drop(ordinal_drop_col,axis=1)
        test_df_nominal=test_df_nominal.drop(nominal_drop_col,axis=1)
        #=====以下為主df刪掉對應欄位=====
        insert_test_df=insert_test_df.drop(list(set(original_df_columns).difference(set(final_column))),axis=1)
        #=====下面這段是處理數值類型變數outlier=====
        outlier_dummy_num=0 #221129 debug for 原先UL跟LL值沒有丟到list中，此數值為從該list中取index的dummy值
        for i, ans in enumerate(numerical_outlier):
            if ans=="yes":   
                outliers_values=df_numerical[df_numerical.columns[i]][(df_numerical[df_numerical.columns[i]]>outlier_UL_list[outlier_dummy_num])|(df_numerical[df_numerical.columns[i]]<outlier_LL_list[outlier_dummy_num])]  #221129 debuf for 原先UL跟LL值沒有丟到list中會導致不會被疊代到       
                test_df_numerical[test_df_numerical.columns[i]]=test_df_numerical[test_df_numerical.columns[i]].replace([outliers_values],np.nan)
                insert_test_df[test_df_numerical.columns[i]]=test_df_numerical[test_df_numerical.columns[i]]
                outlier_dummy_num+=1
        #=====以下開始處理dropna部份=====
        insert_test_df=insert_test_df.dropna(subset=need_dropna_column) #subset用法是只選擇要dropna的欄位做處理就好其餘不動
        insert_test_df=insert_test_df.reset_index(drop=True) #221103要將被dropna的index重設後面才不會有錯
        #=====若有標籤欄位必須在處理完drop欄位與dropna以後將標籤欄位獨立出來避免資料筆數異常=====
        if label_column!='尚未選擇標籤欄位':
            test_df_label=insert_test_df[label_column] 
            insert_test_df=insert_test_df.drop(label_column,axis=1)
        #=====以下開始處理缺失值填補=====
        #=====以下這段目的是要再將做完上述前處理的各類型特徵再拆出 
        test_df_numerical=pd.DataFrame(insert_test_df[test_df_numerical.columns])
        test_df_ordinal=pd.DataFrame(insert_test_df[test_df_ordinal.columns])
        test_df_nominal=pd.DataFrame(insert_test_df[test_df_nominal.columns])
        #=====以下為數值型補值=====
        if fillna_with_mean_list!=[]:
            test_df_numerical[fillna_with_mean_list]= numerical_imputer_mean.transform(test_df_numerical[fillna_with_mean_list])
        if fillna_with_median_list!=[]:
             test_df_numerical[fillna_with_median_list]= numerical_imputer_median.transform(test_df_numerical[fillna_with_median_list])
        #=====以下為有序類別型補值=====
        if ord_fillna_with_mode_list!=[]:
            for i,ob in enumerate(ord_fillna_with_mode_list):
                test_df_ordinal[ob]=test_df_ordinal[ob].fillna(ord_mode_list[i]) 
        if ord_fillna_with_unknown_list!=[]:
            for i in ord_fillna_with_unknown_list:
                test_df_ordinal[i]=test_df_ordinal[i].fillna("Unknown")
        #=====以下為無序類別型補值=====
        if nom_fillna_with_mode_list!=[]:
           for i,ob in enumerate(nom_fillna_with_mode_list):
                test_df_nominal[ob]=test_df_nominal[ob].fillna(nom_mode_list[i]) 
        if nom_fillna_with_unknown_list!=[]:
            for i in nom_fillna_with_unknown_list:
               test_df_nominal[i]=test_df_nominal[i].fillna("Unknown")
        #=====以下為數值屬性特徵標準化=====
        if min_max_col!=[]:
            test_df_min_Max_scaler = preprocessing.MinMaxScaler()
            test_df_min_max=test_df_min_Max_scaler.fit(test_df_numerical[min_max_col])
            test_df_numerical[min_max_col]= test_df_min_max.transform(test_df_numerical[min_max_col])
        if standard_col!=[]:
            test_df_standard_scaler = preprocessing.StandardScaler()
            test_df_standard=test_df_standard_scaler.fit(df_numerical[standard_col])
            test_df_numerical[standard_col]=test_df_standard.transform(test_df_numerical[standard_col])
        #====以下是無序資料直接做one-hot處理====
        test_df_nominal=pd.DataFrame(oh.transform(test_df_nominal).toarray(),columns=oh.get_feature_names_out())#oh.get_feature_names_out()直接將column原本為數字編碼直接變成正確名稱
    #=====以下開始處理有序類別label encoding and one-hot encoding======
        #=====以下這段是自定義label_encoding=====
        if self_define_label_encoding_col!=[]:
            test_df_ord_self_define_label_encoding=pd.DataFrame(test_df_ordinal[self_define_label_encoding_col])
            for c in test_df_ord_self_define_label_encoding.columns:
                test_df_ord_self_define_label_encoding[c] = test_df_ord_self_define_label_encoding[c].map(columnMap)
        #=====以下這段是default label_encoding=====
        if auto_label_encoding_col!=[]:
            test_df_ord_auto_label_encoding=pd.DataFrame(test_df_ordinal[auto_label_encoding_col])
            for c in test_df_ord_auto_label_encoding.columns:
                test_df_ord_auto_label_encoding[c]= labelencoder.transform(test_df_ord_auto_label_encoding[c])
        #=====以下這段是使用者選擇有序類別欄位做one-hot encoding=====
        if one_hot_col!=[]:
            test_df_ord_one_hot=pd.DataFrame(test_df_ordinal[one_hot_col])
            test_df_ord_one_hot=pd.DataFrame(ordinal_oh.transform(test_df_ord_one_hot).toarray(),columns=ordinal_oh.get_feature_names_out())
        #=====將df_ordinal從上面三個情況下整並起來=====
        if self_define_label_encoding_col!=[] and auto_label_encoding_col!=[] and one_hot_col!=[]: #當有序類別同時存在三種處理方法時（label encoding自定義/label encoding default/one-hot)
            test_df_ordinal=pd.concat([test_df_ord_self_define_label_encoding, test_df_ord_auto_label_encoding, test_df_ord_one_hot],axis=1)
    
        elif self_define_label_encoding_col!=[] and auto_label_encoding_col!=[] and one_hot_col==[]:#當有序類別同時存在兩種處理方法時（label encoding自定義/label encoding default)
            test_df_ordinal=pd.concat([test_df_ord_self_define_label_encoding, test_df_ord_auto_label_encoding],axis=1)
        
        elif self_define_label_encoding_col!=[] and auto_label_encoding_col==[] and one_hot_col!=[]:#當有序類別同時存在兩種處理方法時（label encoding自定義/one-hot)
            test_df_ordinal=pd.concat([test_df_ord_self_define_label_encoding, test_df_ord_one_hot],axis=1)
        
        elif self_define_label_encoding_col==[] and auto_label_encoding_col!=[] and one_hot_col!=[]:#當有序類別同時存在兩種處理方法時（label encoding default/one-hot)
            test_df_ordinal=pd.concat([test_df_ord_auto_label_encoding, test_df_ord_one_hot],axis=1)

        elif self_define_label_encoding_col!=[] and auto_label_encoding_col==[] and one_hot_col==[]: #當有序類別僅存在一種處理方法時（label encoding自定義)
            test_df_ordinal=test_df_ord_self_define_label_encoding
        
        elif self_define_label_encoding_col==[] and auto_label_encoding_col!=[] and one_hot_col==[]: #當有序類別僅存在一種處理方法時（label encoding default)
            test_df_ordinal=test_df_ord_auto_label_encoding

        elif self_define_label_encoding_col==[] and auto_label_encoding_col==[] and one_hot_col!=[]: #當有序類別僅存在一種處理方法時（one-hot)
            test_df_ordinal=test_df_ord_one_hot
        
        #=====221121整合時記得加上label欄位有無的判定===== 
        label_column_check= session["label_column"]
        if label_column_check!="尚未選擇標籤欄位": #有標籤欄位存在的前提
            insert_test_df=pd.concat([test_df_numerical,test_df_ordinal,test_df_nominal,test_df_label],axis=1)
            
        else: #沒有標籤欄位的前提
            insert_test_df=pd.concat([test_df_numerical,test_df_ordinal,test_df_nominal],axis=1)      
        #===============================================
        #=====221219 debug for 避免測試資料集因無序類別數量與訓練資料集不一致須擴充欄位=====
        if len(df.columns)!=len(insert_test_df.columns):
            for i in list(set(df.columns).difference(insert_test_df.columns)):
                insert_test_df[i]=0

        insert_test_df=insert_test_df[df.columns] #此行讓測試資料集的欄位順序會變成跟訓練資料集一樣
       
        return insert_test_df

#=====我是函式結束分界線=====

    #=====221123開始丟入測試資料集=====
    test_df_folder_path=session["test_df_folder_path"]
    test_df_filename=session["test_df_filename"]
    test_df2_filename=session["test_df_filename2"]
    test_df3_filename=session["test_df_filename3"]

    if os.path.exists(test_df_folder_path+"/"+test_df_filename):
        df_test=pd.read_csv(test_df_folder_path+"/"+test_df_filename)
        #=====執行函式=====
        df_test=test_df_preprocessing(df_test)
        #=====存檔======
        df_test.to_csv(test_df_folder_path+"/"+test_df_filename[0:-4]+"_after_preprocessing.csv",index=False)
    #==220906加入第2.3測試資料集的處理==
    if os.path.exists(test_df_folder_path+"/"+test_df2_filename):
        df_test2=pd.read_csv(test_df_folder_path+"/"+test_df2_filename)#若檔案存在，則讀取
        #=====執行函式=====
        df_test2=test_df_preprocessing(df_test2)
        #=====存檔======
        df_test2.to_csv(test_df_folder_path+"/"+test_df2_filename[0:-4]+"_after_preprocessing.csv",index=False)
    if os.path.exists(test_df_folder_path+"/"+test_df3_filename):
        df_test3=pd.read_csv(test_df_folder_path+"/"+test_df3_filename)#若檔案存在，則讀取 
        #=====執行函式=====
        df_test3=test_df_preprocessing(df_test3)
        #=====存檔======
        df_test3.to_csv(test_df_folder_path+"/"+test_df3_filename[0:-4]+"_after_preprocessing.csv",index=False)
     
    #========================================================================================================================================
    #=====221129以下為匯出所有前處理參數=====
    json_log={
                    "label_column":label_column ,
                    "numerical_list":numerical_list, #數值屬性特徵欄位
                    "nominal_cata_list":nominal_cata_list, #無序類別屬性特徵欄位
                    "ordinal_cata_list":ordinal_cata_list, #有序類別屬性特徵欄位
                    "numerical_undrop_columns": numerical_undrop_columns, #數值屬性留下的欄位
                    "nominal_undrop_columns":nominal_undrop_columns , #無序類別留下的欄位
                    "ordinal_undrop_columns":ordinal_undrop_columns , #有序類別留下的欄位
                    "final_column": final_column, #最後留下來的總欄位
                    "total_drop_columns": final_drop_columns, #221212新增此欄位以便觀看
                    "numerical_outlier": numerical_outlier,#數值特徵要做outlier的欄位
                    "outlier_UL_list": outlier_UL_list, #將outlier的上限值清單列出
                    "outlier_LL_list": outlier_LL_list, #將outlier的下限值清單列出
                    "need_dropna_column": need_dropna_column, #將需要dropna的欄位列出
                    "fillna_with_mean_list": fillna_with_mean_list, #確認數值特徵補植方式為平均值的欄位
                    "fillna_with_median_list": fillna_with_median_list, #確認數值特徵補植方式為中位數的欄位
                    "imputer_mean_list": imputer_mean_list, #實際填入平均值的值by欄位
                    "imputer_median_list": imputer_median_list, #實際填入中位數的值by欄位
                    "ord_fillna_with_mode_list": ord_fillna_with_mode_list, #有序類別特徵以眾數填補
                    "ord_fillna_with_unknown_list": ord_fillna_with_unknown_list,  #有序類別特徵以unknown填補
                    "nom_fillna_with_mode_list":  nom_fillna_with_mode_list, #無序類別特徵以眾數填補
                    "nom_fillna_with_unknown_list": nom_fillna_with_unknown_list, #無序類別特徵以unknown填補
                    "min_max_col": min_max_col, #數值欄位標準化選擇min_max的欄位
                    "standard_col": standard_col, #數值欄位標準化選擇standard scaler的欄位
                    "ord_columns_handle_with_self_define_label_encoding": self_define_label_encoding_col, #221130紀錄有序類別欄位哪些自定義label_encoding
                    "ord_columns_handle_with_default_label_encoding": auto_label_encoding_col, #221130紀錄有序類別欄位哪些用預設label_encoding
                    "ord_columns_handle_with_one-hot": one_hot_col, #221130紀錄有序類別欄位哪些使用one-hot
                    "self_define_label_encoding": self_define_for_final_json, #221130新增將自定義label encoding加入
                    "default_label_encoding": auto_label_encoding_for_final_json,  #221130新增將default label encoding加入

                }

    #下面class語法參考網址：https://stackoverflow.com/questions/50916422/python-typeerror-object-of-type-int64-is-not-json-serializable
    #原因：因為上面的labelencoder_name_mapping在輸出到json dump時會因為value的屬性問題導致無法寫入故需要下面的class做屬性轉換
    class NpEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return super(NpEncoder, self).default(obj)

    

    with open(fp+"/"+"preprocessing_parameter_log.json", "w",encoding="utf-8") as f: #注意要用encoding="utf-8"以及下面的ensure_ascii=False才可寫入中文
        json.dump(json_log, f,cls=NpEncoder ,indent = 2,ensure_ascii=False) #寫入json檔，注意這邊要套用cls=NpEncoder語法
    #======================================
    return redirect ('/Data_Preprocessing_Results_Check')


@df_pre.route('/Data_Preprocessing_Results_Check')
@login_required
def data_mining():
    #讀取訓練資料集
    fp=session["folder_path"]
    fn=session["filename"]
    df=pd.read_csv(fp+"/"+fn[0:-4]+"_before_encoding.csv")
    #221026確認須將顯示的圖表類與預覽處理後資料集的內容分開避免觀看上的誤會
    df_for_head=pd.read_csv(fp+"/"+fn[0:-4]+"_after_preprocessing.csv")
    df_head=df_for_head.head(50)
    df_head.to_csv("static/tmp/df_head.csv",index=False)
    
    #=====221123新增將處理好的欄位屬性重新定義至與前面定義的相同=====
    dtype_col=session["dtype_col"]#221026發現bug要給處理完後的資料集在顯示出那些統計圖表以前，欄位屬性要與前面定義的相同
    print("原始的dtype_col：",dtype_col)
    drop_col_index=session["drop_col_index"]
    #221123 debug for 前面如果有drop column的話這裡的dtype column必須要刪掉對應欄位
    original_dtype_col_len=len(dtype_col)
    for i,index in enumerate(drop_col_index):
        if len(dtype_col)<original_dtype_col_len:
            index=index-1
            del dtype_col[index]  
        else:
            del dtype_col[i]
    print("新版的dtype_col：",dtype_col)
    #＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
    

    for index_num,col in enumerate(df.columns):    
            df[col]=df[col].astype(dtype_col[index_num])
    #========================================================
    
    #========220901將"數值"屬性特徵做皮爾森特徵heatmap圖========
    int_and_float_list=[]
    for i in df.columns:
        if df[i].dtypes=="int64":
            int_and_float_list.append(i)
        if df[i].dtypes=="float64":
            int_and_float_list.append(i)
    if int_and_float_list!=[]: #221026解bug for 若不存在數值欄位時作圖會有錯
        int_and_float_df_col=df[int_and_float_list]
        colormap = plt.cm.RdBu # 繪圖庫中的顏色查找表。比如A1是紅色,A2是淺藍色。 這樣一種映射關係

        plt.figure(figsize=(14,12))#創建一個新的圖表，參數是尺寸，單位為英寸。
        plt.title("Pearson Correlation of Features", y=1.05, size=15) #給圖表一個標題~~

        sns.heatmap(int_and_float_df_col.astype(float).corr(),linewidths=0.1,vmax=1.0,square=True, cmap=colormap, linecolor="white", annot=True) #將皮爾森係數值畫成圖表形式。
        plt.savefig("static/pic/pearson_heatmap.png", bbox_inches='tight', pad_inches=0.0)
        pearsman=str("static/pic/pearson_heatmap.png")
        plt.close()  # 要記得關閉檔案
        # plt.show() #這裡可以先不show
        #=====================================================
        #=====220901以下測試將數值屬性特徵的describe資訊輸出========
        #print(df.describe()) #檢視表單的數據分佈（中位數/75％/25％等資料）
        #以下將describe轉換成csv檔
        des_df=df.describe().T
        des_df.insert(0, 'column_name', des_df.index )
        # des_df.to_csv("/home/tony/文件/IAML_MLJAR/IAML_version_4_modify/self_test_area/des_df.csv",index=False) #先不用存檔
        column_name=des_df["column_name"].values.tolist()
        count_value=des_df["count"].values.tolist()
        mean_value=des_df["mean"].values.tolist()
        std_value=des_df["std"].values.tolist()
        min_value=des_df["min"].values.tolist()
        df_top25=des_df["25%"].values.tolist()
        df_top50=des_df["50%"].values.tolist()
        df_top75=des_df["75%"].values.tolist()
        max_value=des_df["max"].values.tolist()
    else: #221027 解bug for無數值屬性或類別屬性欄位時會出錯問題
        pearsman=""
        column_name=None
        count_value=None
        mean_value=None
        std_value=None
        min_value=None
        df_top25=None
        df_top50=None
        df_top75=None
        max_value=None
     
    #========220901將"類別"屬性特徵分佈做成圓餅圖========
    obj_list=[]
    for obj in df.columns:
        if df[obj].dtypes=="object":
            obj_list.append(obj)
    if obj_list!=[]: #221026解bug for 若不存在類別欄位時會有錯
        s=1
        # print(obj_list)
        # print("df[obj_list]",df[obj_list].columns)
        plt.figure(figsize=(15,10))
        for i in df[obj_list].columns:
            if len(df[obj_list].columns)<=4:
                pie_source=df[i].value_counts(normalize=True)
                plt.subplot(1, 4, s)
                
                plt.pie(pie_source,                           # 數值
                    labels=pie_source.index,                         # 標籤
                    autopct = "%1.1f%%",                  # 將數值百分比並留到小數點一位
                    pctdistance = 0.6,                    # 數字距圓心的距離
                    textprops = {"fontsize" : 12},        # 文字大小
                    shadow=True)                          # 設定陰影
                #plt.rcParams["font.sans-serif"]="Microsoft JhengHei Boot" #220913參考python初學特訓班的書本，將中文顯示出的方式，適用於windows
                plt.rcParams['font.family'] = 'AR PL UMing CN' #220913 ubuntu可以用的中文化，參考https://dwye.dev/post/matplotlib-font/
                plt.rcParams['axes.unicode_minus'] = False
                plt.axis('equal')                                          # 使圓餅圖比例相等
                plt.title(i, {"fontsize" : 18})  # 設定標題及其文字大小
                plt.legend(loc = "best")                                   # 設定圖例及其位置為最佳
                s=s+1
            elif 5<=len(df[obj_list].columns)<=8:
                pie_source=df[i].value_counts(normalize=True)
                plt.subplot(2, 4, s)
                #plt.rcParams["font.sans-serif"]="Microsoft JhengHei Boot" #220913參考python初學特訓班的書本，將中文顯示出的方式，適用於windows
                plt.rcParams['font.family'] = 'AR PL UMing CN' #220913 ubuntu可以用的中文化，參考https://dwye.dev/post/matplotlib-font/
                plt.rcParams['axes.unicode_minus'] = False
                plt.pie(pie_source,                           # 數值
                    labels=pie_source.index,                         # 標籤
                    autopct = "%1.1f%%",                  # 將數值百分比並留到小數點一位
                    pctdistance = 0.6,                    # 數字距圓心的距離
                    textprops = {"fontsize" : 12},        # 文字大小
                    shadow=True)                          # 設定陰影
                plt.axis('equal')                                          # 使圓餅圖比例相等
                plt.title(i, {"fontsize" : 18})  # 設定標題及其文字大小
                plt.legend(loc = "best")                                   # 設定圖例及其位置為最佳
                s=s+1
            elif 9<=len(df[obj_list].columns)<=12:
                pie_source=df[i].value_counts(normalize=True)
                plt.subplot(3, 4, s)
                #plt.rcParams["font.sans-serif"]="Microsoft JhengHei Boot" #220913參考python初學特訓班的書本，將中文顯示出的方式，適用於windows
                plt.rcParams['font.family'] = 'AR PL UMing CN' #220913 ubuntu可以用的中文化，參考https://dwye.dev/post/matplotlib-font/
                plt.rcParams['axes.unicode_minus'] = False
                plt.pie(pie_source,                           # 數值
                    labels=pie_source.index,                         # 標籤
                    autopct = "%1.1f%%",                  # 將數值百分比並留到小數點一位
                    pctdistance = 0.6,                    # 數字距圓心的距離
                    textprops = {"fontsize" : 12},        # 文字大小
                    shadow=True)                          # 設定陰影
                plt.axis('equal')                                          # 使圓餅圖比例相等
                plt.title(i, {"fontsize" : 18})  # 設定標題及其文字大小
                plt.legend(loc = "best")                                   # 設定圖例及其位置為最佳
                s=s+1

        #plt.suptitle("Catagory Features Pie Chart")
        #plt.show()
        plt.savefig("static/pic/pie_chart.png", bbox_inches='tight', pad_inches=0.0)
        pie=str("static/pic/pie_chart.png")
        plt.close()
    else: #221027 解bug for無數值屬性或類別屬性欄位時會出錯問題
        pie=""

    return render_template("data_preprocessing_results_check.html",pearsman=pearsman,pie=pie,column_name=column_name,count_value=count_value,mean_value=mean_value,std_value=std_value,min_value=min_value,df_top25=df_top25,df_top50=df_top50,df_top75=df_top75,max_value=max_value)

#======220907新增下載處理好的資料集功能=======
@df_pre.route('/df_download') 
@login_required
def df_download():
    fp=session["folder_path"]

    zipf = zipfile.ZipFile(fp+"/"+'download.zip','w', zipfile.ZIP_DEFLATED)
    for root,dirs, files in os.walk(fp):
        for file in files:
            if "_after_preprocessing" in file:
                download_path=os.path.join(fp+"/", file)
                zipf.write(download_path, basename(download_path))
            if ".json" in file: #221027增加類別變數若有label encoding時讓使用者下載編碼對應檔案
                download_path=os.path.join(fp+"/", file)
                zipf.write(download_path, basename(download_path))
    zipf.close()

    download_file=str(fp+"/download.zip")

    return send_file(download_file,as_attachment=True)
#======220907新增預覽資料集功能=======
# @df_pre.route('/df_preview')
# def df_preview():
#     return render_template("df_head.html")


