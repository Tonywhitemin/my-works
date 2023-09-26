
import os
from flask import request
from flask import render_template
from flask import redirect
from flask import session
import pandas as pd
from werkzeug.utils import secure_filename
import shutil
import glob
import re
from flask import Blueprint
from function_login_requirement import login_required

Upload_file= Blueprint("Upload_file",__name__)
UPLOAD_FOLDER = r'static/tmp'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
                  
ALLOWED_EXTENSIONS = set(["csv"]) #允許的副檔名

@Upload_file.route('/homepage',methods=["POST","GET"])
@login_required
def homepage():
    return render_template("homepage.html")

@Upload_file.route('/create_folder',methods=["POST","GET"])
@login_required
def create_folder():
    try:
        if request.method == 'POST':
            folder_name=request.values["folder_name"]
            
            #221014由於發現資料夾名稱若含空白會影響後面機器學習圖片呈現，所以若使用者有輸入空白將在此強迫取消空白
            folder_name=re.sub(r"\s+", "", folder_name)
            account=session["user_account_folder"]
            f_path=os.path.join(UPLOAD_FOLDER,account,folder_name)
            print("f_path為：",f_path)
            session["folder_path"]=f_path
            #＝＝＝＝＝220816測試資料夾名稱衝突時跳出警告視窗＝＝＝＝＝
            try:
                os.mkdir(f_path)
                return render_template("upload_file.html")
            except OSError as exc:
                alarm='錯誤：資料夾名稱已存在，請為專案取其他名稱'
                eng_alarm='Error:The folder name is already exist, please try another one.'
                return render_template("homepage.html",error=alarm,error2=eng_alarm)

            #=========以上220816測試OK============

        
    except Exception as e:
        print(e)
        # f_path = session.get("folder_path", None)
        # if f_path is not None:
        #     shutil.rmtree(f_path)
        # return redirect("/")

@Upload_file.route("/current_file_check",methods=["POST","GET"])
@login_required
def current_file_check():
    file = request.files['file-train']
    f_path=session["folder_path"]
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        #print("filename: ",filename)
        folder_path=session["folder_path"]
        file.save(folder_path+"/"+filename)
        session["folder_path"]=folder_path
        session["filename"]=filename
        fp=session["folder_path"]
        fn=session["filename"]
        #220913新增檢視若檔案編碼不是UTF-8要跳錯誤提醒
        try:
            df=pd.read_csv(fp+"/"+fn)
        except UnicodeDecodeError as e:
            error_for_utf8="訓練資料集檔案編碼格式非UTF-8，請確認格式後重新上傳檔案，謝謝"
            error_for_utf8_eng="Please check the file unicode is UTF-8, thanks!"
            return render_template("upload_file_wrong_encoding.html",error_for_utf8=error_for_utf8,error_for_utf8_eng=error_for_utf8_eng)
        
        #==以下為欄位list==
        features_list=[]
        for i in df.columns:
            features_list.append(i)

        # for i in range(len(df_missing_rate["column_name"])):
        #     features_list.append(df_missing_rate.iloc[i,1])
        #print(features_list)
        
        #====以下為顯示現有欄位屬性220902修正顯示項目為中文====
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
        #========
    else:
        error_for_train_df_format='Error:訓練資料集檔案格式錯誤'
        err_eng="Please check:The Filename Extension is .csv"

        return render_template("upload_file_wrong_format.html",error_for_df_format=error_for_train_df_format,err_eng=err_eng)

  

    #=========220817加入測試資料集的檔案確認與儲存功能========
    yes_or_no_test_df=request.values["yes_or_no_test_df"]
    if yes_or_no_test_df=="yes":
        #=================================220905新增可上傳多個測試資料集=======================================
        test_df_num=request.values["test_df_num"]
        if test_df_num=="1":
            file_test_1 = request.files['file-test-1']
            if file_test_1 and allowed_file(file_test_1.filename):
                test_df_filename = secure_filename(file_test_1.filename)#220926修改原始碼以克服無法上傳中文檔名的問題，參考網址：https://juejin.cn/post/6984687937036222471
                #print("Test Dataset filename: ",test_df_filename)
                test_df_folder_path=session["folder_path"]
                file_test_1.save(test_df_folder_path+"/"+test_df_filename)
                session["test_df_folder_path"]=test_df_folder_path
                session["test_df_filename"]=test_df_filename
                #====220913增加確認檔案編碼不是UTF-8時跳錯誤====
                try:
                    df_test=pd.read_csv(test_df_folder_path+"/"+test_df_filename)
                except UnicodeDecodeError as e:
                    error_for_utf8="驗證資料集檔案編碼格式非UTF-8，請確認格式後重新上傳檔案，謝謝"
                    error_for_utf8_eng="Please check the file unicode is UTF-8, thanks!"
                    return render_template("upload_file_wrong_encoding.html",error_for_utf8=error_for_utf8,error_for_utf8_eng=error_for_utf8_eng)
                #====220905檢查測試資料集特徵數量與名稱是否一致====
                test_df_features_list=[]
                for i in df_test.columns:
                    test_df_features_list.append(i)
                if test_df_features_list!=features_list:
                    f_path=session["folder_path"]
                    to_be_deleted_csv_files = glob.glob(f_path+"/*.csv")
                    for file in to_be_deleted_csv_files:
                        try:
                            os.remove(file)
                        except OSError as e:
                            print(f"Error:{ e.strerror}")
                    error_for_features_didnt_match='Error:測試資料集欄位數量或名稱不一致'
                    error_for_features_didnt_match_eng='Please check the format between train dataset and test dataset,thanks!'
                    return render_template("upload_file_test_df_columns_not_match.html",
                    error_for_features_didnt_match=error_for_features_didnt_match,error_for_features_didnt_match_eng=error_for_features_didnt_match_eng)
                    
                #============================================
                session["test_df_filename2"]="不該存在的檔案2" #避免後面出錯先給一個不存在的路徑
                session["test_df_filename3"]="不該存在的檔案3" #避免後面出錯先給一個不存在的路徑
                return render_template("dataset_current_info.html",l1=features_list, j1=features_dtype_list) 
            else:
                #shutil.rmtree(f_path)
                to_be_deleted_csv_files = glob.glob(f_path+"/*.csv")
                for file in to_be_deleted_csv_files:
                    try:
                        os.remove(file)
                    except OSError as e:
                        print(f"Error:{ e.strerror}")
                error_for_train_df_format='Error:測試資料集檔案格式錯誤'
                err_eng="Please check:The Filename Extension is .csv"

                return render_template("upload_file_wrong_format.html",error_for_df_format=error_for_train_df_format,err_eng=err_eng)
                
                
        #=================以下為當有2個測試資料集時的處理==========================
        elif test_df_num=="2":
            file_test_1 = request.files['file-test-2-1']
            file_test_2 = request.files['file-test-2-2']
            if file_test_1 and allowed_file(file_test_1.filename):
                test_df_filename = secure_filename(file_test_1.filename)
                #print("Test Dataset filename: ",test_df_filename)
                test_df_folder_path=session["folder_path"]
                file_test_1.save(test_df_folder_path+"/"+test_df_filename)
                session["test_df_folder_path"]=test_df_folder_path
                session["test_df_filename"]=test_df_filename
                #====220913增加確認檔案編碼不是UTF-8時跳錯誤====
                try:
                    df_test=pd.read_csv(test_df_folder_path+"/"+test_df_filename)
                except UnicodeDecodeError as e:
                    error_for_utf8="第一個驗證資料集檔案編碼格式非UTF-8，請確認格式後重新上傳檔案，謝謝"
                    error_for_utf8_eng="Please check the file unicode is UTF-8, thanks!"
                    return render_template("upload_file_wrong_encoding.html",error_for_utf8=error_for_utf8,error_for_utf8_eng=error_for_utf8_eng)
                #====220905檢查測試資料集特徵數量與名稱是否一致====
               
                test_df_features_list=[]
                for i in df_test.columns:
                    test_df_features_list.append(i)
                if test_df_features_list!=features_list:
                    f_path=session["folder_path"]
                    to_be_deleted_csv_files = glob.glob(f_path+"/*.csv")
                    for file in to_be_deleted_csv_files:
                        try:
                            os.remove(file)
                        except OSError as e:
                            print(f"Error:{ e.strerror}")
                    error_for_features_didnt_match='Error:第一個測試資料集欄位數量或名稱不一致'
                    error_for_features_didnt_match_eng='Please check the format between train dataset and test dataset,thanks!'
                    return render_template("upload_file_test_df_columns_not_match.html",
                    error_for_features_didnt_match=error_for_features_didnt_match,error_for_features_didnt_match_eng=error_for_features_didnt_match_eng)
                #============================================
            else:
                to_be_deleted_csv_files = glob.glob(f_path+"/*.csv")
                for file in to_be_deleted_csv_files:
                    try:
                        os.remove(file)
                    except OSError as e:
                        print(f"Error:{ e.strerror}")
                error_for_train_df_format='Error:第一個測試資料集檔案格式錯誤'
                err_eng="Please check:The Filename Extension is .csv"

                return render_template("upload_file_wrong_format.html",error_for_df_format=error_for_train_df_format,err_eng=err_eng)

            if file_test_2 and allowed_file(file_test_2.filename):
                test_df_filename2 = secure_filename(file_test_2.filename)
                #print("Test Dataset filename: ",test_df_filename)
                test_df_folder_path=session["folder_path"]
                file_test_2.save(test_df_folder_path+"/"+test_df_filename2)
                session["test_df_folder_path"]=test_df_folder_path
                session["test_df_filename2"]=test_df_filename2
                #====220913增加確認檔案編碼不是UTF-8時跳錯誤====
                try:
                    df_test2=pd.read_csv(test_df_folder_path+"/"+test_df_filename2)
                except UnicodeDecodeError as e:
                    error_for_utf8="第二個驗證資料集檔案編碼格式非UTF-8，請確認格式後重新上傳檔案，謝謝"
                    error_for_utf8_eng="Please check the file unicode is UTF-8, thanks!"
                    return render_template("upload_file_wrong_encoding.html",error_for_utf8=error_for_utf8,error_for_utf8_eng=error_for_utf8_eng)
                #====220905檢查測試資料集特徵數量與名稱是否一致====
                
                test_df2_features_list=[]
                for i in df_test2.columns:
                    test_df2_features_list.append(i)
                if test_df2_features_list!=features_list:
                    f_path=session["folder_path"]
                    to_be_deleted_csv_files = glob.glob(f_path+"/*.csv")
                    for file in to_be_deleted_csv_files:
                        try:
                            os.remove(file)
                        except OSError as e:
                            print(f"Error:{ e.strerror}")
                    error_for_features_didnt_match='Error:第二個測試資料集欄位數量或名稱不一致'
                    error_for_features_didnt_match_eng='Please check the format between train dataset and test dataset,thanks!'
                    return render_template("upload_file_test_df_columns_not_match.html",
                    error_for_features_didnt_match=error_for_features_didnt_match,error_for_features_didnt_match_eng=error_for_features_didnt_match_eng)
                    
                   

                #============================================
                session["test_df_filename3"]="不該存在的檔案3" #避免後面出錯先給一個不存在的路徑
                return render_template("dataset_current_info.html",l1=features_list, j1=features_dtype_list) 
            else:
                to_be_deleted_csv_files = glob.glob(f_path+"/*.csv")
                for file in to_be_deleted_csv_files:
                    try:
                        os.remove(file)
                    except OSError as e:
                        print(f"Error:{ e.strerror}")
                error_for_train_df_format='Error:第二個測試資料集檔案格式錯誤'
                err_eng="Please check:The Filename Extension is .csv"

                return render_template("upload_file_wrong_format.html",error_for_df_format=error_for_train_df_format,err_eng=err_eng)

        #==============以下為3個測試資料集上傳時的處理======================
        elif test_df_num=="3":
            file_test_1 = request.files['file-test-3-1']
            file_test_2 = request.files['file-test-3-2']
            file_test_3 = request.files['file-test-3-3']
            if file_test_1 and allowed_file(file_test_1.filename):
                test_df_filename = secure_filename(file_test_1.filename)
                #print("Test Dataset filename: ",test_df_filename)
                test_df_folder_path=session["folder_path"]
                file_test_1.save(test_df_folder_path+"/"+test_df_filename)
                session["test_df_folder_path"]=test_df_folder_path
                session["test_df_filename"]=test_df_filename
                #====220913增加確認檔案編碼不是UTF-8時跳錯誤====
                try:
                    df_test=pd.read_csv(test_df_folder_path+"/"+test_df_filename)
                except UnicodeDecodeError as e:
                    error_for_utf8="第一個驗證資料集檔案編碼格式非UTF-8，請確認格式後重新上傳檔案，謝謝"
                    error_for_utf8_eng="Please check the file unicode is UTF-8, thanks!"
                    return render_template("upload_file_wrong_encoding.html",error_for_utf8=error_for_utf8,error_for_utf8_eng=error_for_utf8_eng)
                #====220905檢查測試資料集特徵數量與名稱是否一致====
                test_df_features_list=[]
                for i in df_test.columns:
                    test_df_features_list.append(i)
                if test_df_features_list!=features_list:
                    f_path=session["folder_path"]
                    to_be_deleted_csv_files = glob.glob(f_path+"/*.csv")
                    for file in to_be_deleted_csv_files:
                        try:
                            os.remove(file)
                        except OSError as e:
                            print(f"Error:{ e.strerror}")
                    error_for_features_didnt_match='Error:第一個測試資料集欄位數量或名稱不一致'
                    error_for_features_didnt_match_eng='Please check the format between train dataset and test dataset,thanks!'
                    return render_template("upload_file_test_df_columns_not_match.html",
                    error_for_features_didnt_match=error_for_features_didnt_match,error_for_features_didnt_match_eng=error_for_features_didnt_match_eng)

                #============================================
            else:
                to_be_deleted_csv_files = glob.glob(f_path+"/*.csv")
                for file in to_be_deleted_csv_files:
                    try:
                        os.remove(file)
                    except OSError as e:
                        print(f"Error:{ e.strerror}")
                error_for_train_df_format='Error:第一個測試資料集檔案格式錯誤'
                err_eng="Please check:The Filename Extension is .csv"

                return render_template("upload_file_wrong_format.html",error_for_df_format=error_for_train_df_format,err_eng=err_eng)

            if file_test_2 and allowed_file(file_test_2.filename):
                test_df_filename2 = secure_filename(file_test_2.filename)
                #print("Test Dataset filename: ",test_df_filename)
                test_df_folder_path=session["folder_path"]
                file_test_2.save(test_df_folder_path+"/"+test_df_filename2)
                session["test_df_folder_path"]=test_df_folder_path
                session["test_df_filename2"]=test_df_filename2
                #====220913增加確認檔案編碼不是UTF-8時跳錯誤====
                try:
                    df_test2=pd.read_csv(test_df_folder_path+"/"+test_df_filename2)
                except UnicodeDecodeError as e:
                    error_for_utf8="第二個驗證資料集檔案編碼格式非UTF-8，請確認格式後重新上傳檔案，謝謝"
                    error_for_utf8_eng="Please check the file unicode is UTF-8, thanks!"
                    return render_template("upload_file_wrong_encoding.html",error_for_utf8=error_for_utf8,error_for_utf8_eng=error_for_utf8_eng)
                #====220905檢查測試資料集特徵數量與名稱是否一致====
                
                test_df2_features_list=[]
                for i in df_test2.columns:
                    test_df2_features_list.append(i)
                if test_df2_features_list!=features_list:
                    f_path=session["folder_path"]
                    to_be_deleted_csv_files = glob.glob(f_path+"/*.csv")
                    for file in to_be_deleted_csv_files:
                        try:
                            os.remove(file)
                        except OSError as e:
                            print(f"Error:{ e.strerror}")
                    error_for_features_didnt_match='Error:第二個測試資料集欄位數量或名稱不一致'
                    error_for_features_didnt_match_eng='Please check the format between train dataset and test dataset,thanks!'
                    return render_template("upload_file_test_df_columns_not_match.html",
                    error_for_features_didnt_match=error_for_features_didnt_match,error_for_features_didnt_match_eng=error_for_features_didnt_match_eng)
                #============================================
            
            else:
                to_be_deleted_csv_files = glob.glob(f_path+"/*.csv")
                for file in to_be_deleted_csv_files:
                    try:
                        os.remove(file)
                    except OSError as e:
                        print(f"Error:{ e.strerror}")
                error_for_train_df_format='Error:第二個測試資料集檔案格式錯誤'
                err_eng="Please check:The Filename Extension is .csv"

                return render_template("upload_file_wrong_format.html",error_for_df_format=error_for_train_df_format,err_eng=err_eng)


            if file_test_3 and allowed_file(file_test_3.filename):
                test_df_filename3 = secure_filename(file_test_3.filename)
                #print("Test Dataset filename: ",test_df_filename)
                test_df_folder_path=session["folder_path"]
                file_test_3.save(test_df_folder_path+"/"+test_df_filename3)
                session["test_df_folder_path"]=test_df_folder_path
                session["test_df_filename3"]=test_df_filename3
                #====220913增加確認檔案編碼不是UTF-8時跳錯誤====
                try:
                    df_test3=pd.read_csv(test_df_folder_path+"/"+test_df_filename3)
                except UnicodeDecodeError as e:
                    error_for_utf8="第三個驗證資料集檔案編碼格式非UTF-8，請確認格式後重新上傳檔案，謝謝"
                    error_for_utf8_eng="Please check the file unicode is UTF-8, thanks!"
                    return render_template("upload_file_wrong_encoding.html",error_for_utf8=error_for_utf8,error_for_utf8_eng=error_for_utf8_eng)
                #====220905檢查測試資料集特徵數量與名稱是否一致====
                
                test_df3_features_list=[]
                for i in df_test3.columns:
                    test_df3_features_list.append(i)
                if test_df3_features_list!=features_list:
                    f_path=session["folder_path"]
                    to_be_deleted_csv_files = glob.glob(f_path+"/*.csv")
                    for file in to_be_deleted_csv_files:
                        try:
                            os.remove(file)
                        except OSError as e:
                            print(f"Error:{ e.strerror}")
                    error_for_features_didnt_match='Error:第三個測試資料集欄位數量或名稱不一致'
                    error_for_features_didnt_match_eng='Please check the format between train dataset and test dataset,thanks!'
                    return render_template("upload_file_test_df_columns_not_match.html",
                    error_for_features_didnt_match=error_for_features_didnt_match,error_for_features_didnt_match_eng=error_for_features_didnt_match_eng)

                #============================================
            
                return render_template("dataset_current_info.html",l1=features_list, j1=features_dtype_list) 
            else:
                to_be_deleted_csv_files = glob.glob(f_path+"/*.csv")
                for file in to_be_deleted_csv_files:
                    try:
                        os.remove(file)
                    except OSError as e:
                        print(f"Error:{ e.strerror}")
                error_for_train_df_format='Error:第三個測試資料集檔案格式錯誤'
                err_eng="Please check:The Filename Extension is .csv"

                return render_template("upload_file_wrong_format.html",error_for_df_format=error_for_train_df_format,err_eng=err_eng)



            
    else: #此處目的為刪除上一次的session資料，避免產生錯誤
        session["test_df_folder_path"]="不該存在的路徑"
        session["test_df_filename"]="不該存在的檔案"
        session["test_df_filename2"]="不該存在的檔案2"
        session["test_df_filename3"]="不該存在的檔案3"
    #======================以上測試OK==========================
    return render_template("dataset_current_info.html",l1=features_list, j1=features_dtype_list,)


