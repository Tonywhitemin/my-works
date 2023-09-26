from flask import session
from flask import Blueprint
from flask import request
from flask import render_template
from flask import send_file
from flask import redirect
from flask import session
from flask import send_file
import os
import pandas as pd
import pandas as pd 
from sklearn.metrics import mean_absolute_error, mean_squared_error,r2_score #回歸指標，RMSE用法mean_squared_error(y_true, y_pred, squared=False)
from sklearn.metrics import roc_auc_score, accuracy_score,f1_score,log_loss #分類指標
# from sklearn.model_selection import train_test_split
# mljar-supervised package
from supervised.automl import AutoML
import matplotlib
matplotlib.use("Agg")
import zipfile
from os.path import basename
from function_login_requirement import login_required



ML= Blueprint("ML",__name__)
ML.secret_key="tttttiiiiii" #session套件必要的指令，但內容可以隨意取

@ML.route('/machine_learining_mode_select',methods=["POST","GET"])
@login_required
def machine_learining_model_select():
    #221003新增判定若標籤欄位數量大於2時預設任務欄位不可選擇binary
    fp=session["folder_path"]
    fn=session["filename"]
    df=pd.read_csv(fp+"/"+fn[0:-4]+"_after_preprocessing.csv")
    label_column=session["label_column"]
    label_set_check=len(set(df[label_column]))
    if label_column!="尚未選擇標籤欄位":
        return render_template("ml_mode_select.html",label_set_check=label_set_check)
    else:
        return render_template("unsupervised.html")

#==================220922開始刻後端接收參數值==============================
@ML.route('/ML_para_accept',methods=["POST","GET"])
@login_required
def ML_para_accept():
    super_or_unsuper=request.values["super_or_unsuper"]
    if super_or_unsuper=="監督式學習":
        super_mission_type=request.values["super_mission_type"]#任務類型
        
        if super_mission_type=="regression":
            session["ml_task"]=super_mission_type
            super_regression_eva=request.values["super_regression_eva"]#評價指標
            session["super_regression_eva"]=super_regression_eva
            super_mission_type="回歸任務" #呈現到前端顯示用
            binary_class_eva=""#為了不要刻太多HTML，讓前端用if/else判斷式讀值即可
            session["binary_class_eva"]=""
            multi_class_eva=""
            session["multi_class_eva"]=""
           
        elif super_mission_type=="binary_classification":
            session["ml_task"]=super_mission_type
            binary_class_eva=request.values["binary_class_eva"]#評價指標
            session["binary_class_eva"]=binary_class_eva
            super_mission_type="二元分類" #呈現到前端顯示用
            multi_class_eva=""
            session["multi_class_eva"]=""
            super_regression_eva=""
            session["super_regression_eva"]=""

        elif super_mission_type=="multiclass_classification":
            session["ml_task"]=super_mission_type
            multi_class_eva=request.values["multi_class_eva"]#評價指標
            session["multi_class_eva"]=multi_class_eva
            super_mission_type="多元分類" #呈現到前端顯示用
            super_regression_eva=""
            session["super_regression_eva"]=""
            binary_class_eva=""
            session["binary_class_eva"]=""
        
        mode_select=request.values["mode_select"]
        if mode_select=="快速模式":
            session["mode"]="Explain"
            fn=session["filename"]
            label_column=session["label_column"]
            return render_template("explain_mode_check.html",super_or_unsuper=super_or_unsuper,super_mission_type=super_mission_type,
                                    mode_select=mode_select,
                                    super_regression_eva=super_regression_eva,binary_class_eva=binary_class_eva,multi_class_eva=multi_class_eva,
                                    train_df_name=fn,train_label=label_column
                                    )

        elif mode_select=="自定義模式":
            session["mode"]="Compete"
            algorithms=request.form.getlist("algorithms")
            session["algorithms"]=algorithms
            train_ensemble=request.values["train_ensemble"]
            if train_ensemble=="1":
                session["train_ensemble"]=True
                train_ensemble="是"#回饋給前端用
            else:
                session["train_ensemble"]=False 
                train_ensemble="否"#回饋給前端用     

            stack_models=request.values["stack_models"]
            if stack_models=="1":
                session["stack_models"]=True
                stack_models="是"#回饋給前端用   
            else:
                session["stack_models"]=False
                stack_models="否" #回饋給前端用 
            
            validation_type=request.values["validation_type"]
            session["validation_type"]=validation_type
            if validation_type=="split":
                vali_split=request.values["vali_split"]
                vali_split=float(vali_split)
                session["vali_split"]=vali_split
                vali_split=str(int(vali_split*100))+"% / "+str(int(round((1-vali_split)*100)))+"%"
                validation_type="Train/Test Split" #回饋給前端用 
                session["vali_k_folds"]=""
                vali_k_folds=""#節省HTML刻劃時間
            elif validation_type=="kfold":
                vali_k_folds=request.values["vali_k_folds"]
                vali_k_folds=int(vali_k_folds)
                session["vali_k_folds"]=vali_k_folds
                session["vali_split"]=""
                vali_split=""#節省HTML刻劃時間

            Golden_Features=request.values["Golden_Features"]
            if Golden_Features=="1":
                session["Golden_Features"]=True
                Golden_Features="是" #回饋給前端用 
            else:
                session["Golden_Features"]=False
                Golden_Features="否" #回饋給前端用

            features_selection=request.values["features_selection"]
            if features_selection=="1":
                session["features_selection"]=True
                features_selection="是" #回饋給前端用
            else:
                session["features_selection"]=False
                features_selection="否" #回饋給前端用

            start_random_models=request.values["start_random_models"]
            start_random_models=int(start_random_models)
            session["start_random_models"]=start_random_models
            start_random_models=str(start_random_models)+"次"#回饋給前端用

            hill_climbing_steps=request.values["hill_climbing_steps"]
            hill_climbing_steps=int(hill_climbing_steps)
            session["hill_climbing_steps"]=hill_climbing_steps
            hill_climbing_steps=str(hill_climbing_steps)+"次"#回饋給前端用

            fn=session["filename"]
            label_column=session["label_column"]

            return render_template("compete_mode_check.html",super_or_unsuper=super_or_unsuper,super_mission_type=super_mission_type,
                                    mode_select=mode_select,
                                    super_regression_eva=super_regression_eva,binary_class_eva=binary_class_eva,multi_class_eva=multi_class_eva,
                                    algorithms=algorithms,train_ensemble=train_ensemble,stack_models=stack_models,validation_type=validation_type,
                                    vali_split=vali_split,vali_k_folds=vali_k_folds,Golden_Features=Golden_Features,features_selection=features_selection,
                                    start_random_models=start_random_models,hill_climbing_steps=hill_climbing_steps,
                                    train_df_name=fn,train_label=label_column
                                    )
            
    else:#送到非監督式學習去
        return redirect("/unsuper")
    #=====================================================

@ML.route("/MLJAR_connect_compete",methods=["post"])#當使用者選定自定義模式會跳轉至這裡
@login_required
def MLJAR_connect_compete():
    #讀取訓練資料集與分割XY
    fp=session["folder_path"]
    fn=session["filename"]
    ML_folder_name="AutoML"
    os.mkdir(fp+"/"+ML_folder_name)
    df=pd.read_csv(fp+"/"+fn[0:-4]+"_after_preprocessing.csv")
    label_column=session["label_column"]
    x=df.drop(label_column,axis=1)
    y=df[label_column]
    #開始抓取MLJAR需要參數
    super_mission_type=session["ml_task"]
    super_regression_eva=session["super_regression_eva"] #評價指標三者只會有一個存在，其餘為空值
    binary_class_eva=session["binary_class_eva"] #評價指標三者只會有一個存在，其餘為空值
    multi_class_eva=session["multi_class_eva"] #評價指標三者只會有一個存在，其餘為空值
    if super_regression_eva!="":
        eval_metric=super_regression_eva
    elif binary_class_eva!="":
        eval_metric=binary_class_eva
    elif multi_class_eva!="":
        eval_metric=multi_class_eva
    session["eval_metric"]=eval_metric
    algorithms=session["algorithms"]
    train_ensemble=session["train_ensemble"]
    stack_models=session["stack_models"]
    Golden_Features=session["Golden_Features"]
    features_selection=session["features_selection"]
    start_random_models=session["start_random_models"]
    hill_climbing_steps=session["hill_climbing_steps"]
    validation_type=session["validation_type"]
    if validation_type=="split":
        vali_split=session["vali_split"]
        vali_split=float(vali_split)
        #220927加入MLJAR段落
        automl = AutoML(
                results_path=fp+"/"+ML_folder_name,
                ml_task=super_mission_type,
                mode="Compete",
                eval_metric=eval_metric,
                train_ensemble=train_ensemble,
                stack_models=stack_models,
                explain_level=2,
                golden_features=Golden_Features,
                features_selection=features_selection,
                start_random_models=start_random_models,
                hill_climbing_steps=hill_climbing_steps,
                validation_strategy={
                "validation_type": validation_type,
                "train_ratio":vali_split,
                "shuffle": True,
                "stratify": True,
                },
                algorithms=algorithms,
                )
        
    elif validation_type=="kfold":
        vali_k_folds=session["vali_k_folds"]
        vali_k_folds=int(vali_k_folds)
        automl = AutoML(
                results_path=fp+"/"+ML_folder_name,
                ml_task=super_mission_type,
                mode="Compete",
                eval_metric=eval_metric,
                train_ensemble=train_ensemble,
                stack_models=stack_models,
                explain_level=1,
                kmeans_features=False,
                golden_features=Golden_Features,
                features_selection=features_selection,
                start_random_models=start_random_models,
                hill_climbing_steps=hill_climbing_steps,
                validation_strategy={
                "validation_type": validation_type,
                "k_folds": vali_k_folds,
                "shuffle": True,
                "stratify": True,
                },
                algorithms=algorithms,
                )

    
    automl.fit(x, y)
    #221003增加讀取leader_board.csv檔案
    lb=pd.read_csv(fp+"/"+ML_folder_name+"/leaderboard.csv")
    name=lb["name"].values.tolist()
    model_type=lb["model_type"].values.tolist()
    metric_type=lb["metric_type"].values.tolist()
    metric_value=lb["metric_value"].values.tolist()
    train_time=lb["train_time"].values.tolist()
    #221003增加以下總表類圖片顯示
    features_heatmap=str(fp+"/"+ML_folder_name+"/features_heatmap.png")#features_heatmap.png
    ldb_performance_boxplot=str(fp+"/"+ML_folder_name+"/ldb_performance_boxplot.png")
    correlation_heatmap=str(fp+"/"+ML_folder_name+"/correlation_heatmap.png")
    #221004新增最佳模型的資料輸出
    eval_metric=session["eval_metric"]
    if eval_metric!=["mae","rmse","logloss"]:
        sort_df = lb.nlargest(1, "metric_value").iloc[0] #會從leaderboard.csv中抓出表現越大的
    else:
        sort_df = lb.nsmallest(1, "metric_value").iloc[0] #會從leaderboard.csv中抓出表現最小的
    target_folder=str(fp+"/"+ML_folder_name+"/"+sort_df["name"])
    super_mission_type=session["ml_task"]
    if super_mission_type=="regression": #221004因回歸與分類任務顯示的圖片不同所以要分開
        pic1=str(target_folder+"/"+"permutation_importance.png")
        pic3=str(target_folder+"/"+"predicted_vs_residuals.png")
        pic4=str(target_folder+"/"+"true_vs_predicted.png")
    else:
        pic1=str(target_folder+"/"+"confusion_matrix.png")
        pic3=str(target_folder+"/"+"permutation_importance.png")
        pic4=str(target_folder+"/"+"roc_curve.png")
        
    #221013新增因kfold方法會產生不同檔名所以要變更檔名
    if validation_type!="kfold":
        validation_result=str(target_folder+"/"+"predictions_validation.csv")
    else:
        validation_result=str(target_folder+"/"+"predictions_out_of_folds.csv")

    #======221011測試新增預測測試資料集======
    
    test_df_folder_path=session["test_df_folder_path"]
    test_df_filename=session["test_df_filename"]
    test_df_filename2=session["test_df_filename2"]
    test_df_filename3=session["test_df_filename3"]
    if test_df_filename3!="不該存在的檔案3":#假設使用者最多上傳三個測試資料集
        test_df_num=3
        df_test=pd.read_csv(test_df_folder_path+"/"+test_df_filename[0:-4]+"_after_preprocessing.csv")
        df_test_X=df_test.drop(label_column,axis=1)
        df_test_y=df_test[label_column]
        
        df_test2=pd.read_csv(test_df_folder_path+"/"+test_df_filename2[0:-4]+"_after_preprocessing.csv")
        df_test2_X=df_test2.drop(label_column,axis=1)
        df_test2_y=df_test2[label_column]

        df_test3=pd.read_csv(test_df_folder_path+"/"+test_df_filename3[0:-4]+"_after_preprocessing.csv")
        df_test3_X=df_test3.drop(label_column,axis=1)
        df_test3_y=df_test3[label_column]

        automl = AutoML(results_path=fp+"/"+ML_folder_name) #用模型預測
        df_test_predictions = automl.predict_all(df_test_X)
        df_test_predictions.to_csv(fp+"/"+ML_folder_name+"/"+test_df_filename[0:-4]+"_predict_propa.csv",index=False)
        
        df_test2_predictions = automl.predict_all(df_test2_X)
        df_test2_predictions.to_csv(fp+"/"+ML_folder_name+"/"+test_df_filename2[0:-4]+"_predict_propa.csv",index=False)
        
        df_test3_predictions = automl.predict_all(df_test3_X)
        df_test3_predictions.to_csv(fp+"/"+ML_folder_name+"/"+test_df_filename3[0:-4]+"_predict_propa.csv",index=False)
        
        df_test_predictions_file=str(fp+"/"+ML_folder_name+"/"+test_df_filename[0:-4]+"_predict_propa.csv")
        df_test2_predictions_file=str(fp+"/"+ML_folder_name+"/"+test_df_filename2[0:-4]+"_predict_propa.csv")
        df_test3_predictions_file=str(fp+"/"+ML_folder_name+"/"+test_df_filename3[0:-4]+"_predict_propa.csv")
        if eval_metric=="rmse":
            df_test_eval_metric=mean_squared_error(df_test_y, df_test_predictions["label"].astype(int), squared=False)
            df_test2_eval_metric=mean_squared_error(df_test2_y, df_test2_predictions["label"].astype(int), squared=False)
            df_test3_eval_metric=mean_squared_error(df_test3_y, df_test3_predictions["label"].astype(int), squared=False)
        elif eval_metric=="mse":
            df_test_eval_metric=mean_squared_error(df_test_y, df_test_predictions["label"].astype(int))
            df_test2_eval_metric=mean_squared_error(df_test2_y, df_test2_predictions["label"].astype(int))
            df_test3_eval_metric=mean_squared_error(df_test3_y, df_test3_predictions["label"].astype(int))
        elif eval_metric=="mae":
            df_test_eval_metric=mean_absolute_error(df_test_y, df_test_predictions["label"].astype(int))
            df_test2_eval_metric=mean_absolute_error(df_test2_y, df_test2_predictions["label"].astype(int))
            df_test3_eval_metric=mean_absolute_error(df_test3_y, df_test3_predictions["label"].astype(int))
        elif eval_metric=="r2":
            df_test_eval_metric=r2_score(df_test_y, df_test_predictions["label"].astype(int))
            df_test2_eval_metric=r2_score(df_test2_y, df_test2_predictions["label"].astype(int))
            df_test3_eval_metric=r2_score(df_test3_y, df_test3_predictions["label"].astype(int))
        elif eval_metric=="logloss":
            df_test_eval_metric=log_loss(df_test_y, df_test_predictions["label"].astype(int))
            df_test2_eval_metric=log_loss(df_test2_y, df_test2_predictions["label"].astype(int))
            df_test3_eval_metric=log_loss(df_test3_y, df_test3_predictions["label"].astype(int))
        elif eval_metric=="auc":
            df_test_eval_metric=roc_auc_score(df_test_y, df_test_predictions["prediction_1"])
            df_test2_eval_metric=roc_auc_score(df_test2_y, df_test2_predictions["prediction_1"])
            df_test3_eval_metric=roc_auc_score(df_test3_y, df_test3_predictions["prediction_1"])
        elif eval_metric=="f1":
            df_test_eval_metric=f1_score(df_test_y, df_test_predictions["label"].astype(int))
            df_test2_eval_metric=f1_score(df_test2_y, df_test2_predictions["label"].astype(int))
            df_test3_eval_metric=f1_score(df_test3_y, df_test3_predictions["label"].astype(int))
        elif eval_metric=="accuracy":
            df_test_eval_metric=accuracy_score(df_test_y, df_test_predictions["label"].astype(int))
            df_test2_eval_metric=accuracy_score(df_test2_y, df_test2_predictions["label"].astype(int))
            df_test3_eval_metric=accuracy_score(df_test3_y, df_test3_predictions["label"].astype(int))
        return render_template("page_after_Auto_ML.html",
        super_mission_type=super_mission_type,#因前端要依據任務類型不同回饋不同項目，故此處要有一個宣告
        name=name,model_type=model_type,metric_type=metric_type,metric_value=metric_value,train_time=train_time,#這行是輸出leaderboard資料用
        features_heatmap=features_heatmap,ldb_performance_boxplot=ldb_performance_boxplot,correlation_heatmap=correlation_heatmap,#這行是輸出總表類圖片用
        pic1=pic1,pic3=pic3,pic4=pic4, #最佳表現資料模型的圖片預覽
        validation_result=validation_result,#最佳模型預測validation資料集的或然率結果csv檔
        test_df_num=test_df_num,#宣告測試資料集數量給前端以利展示預測結果
        eval_metric=eval_metric,#回饋前端顯示評價指標名稱
        df_test_eval_metric=df_test_eval_metric,df_test2_eval_metric=df_test2_eval_metric,df_test3_eval_metric=df_test3_eval_metric,#221012增加測試資料集的預測結果的評價指標
        df_test_predictions_file=df_test_predictions_file,df_test2_predictions_file=df_test2_predictions_file,df_test3_predictions_file=df_test3_predictions_file,#221012增加下載測試資料集的預測結果檔案路徑
        )
    elif test_df_filename2!="不該存在的檔案2": #假設使用者上傳兩個測試資料集
        test_df_num=2
        df_test=pd.read_csv(test_df_folder_path+"/"+test_df_filename[0:-4]+"_after_preprocessing.csv")
        df_test_X=df_test.drop(label_column,axis=1)
        df_test_y=df_test[label_column]

        df_test2=pd.read_csv(test_df_folder_path+"/"+test_df_filename2[0:-4]+"_after_preprocessing.csv")
        df_test2_X=df_test2.drop(label_column,axis=1)
        df_test2_y=df_test2[label_column]

        automl = AutoML(results_path=fp+"/"+ML_folder_name) #用模型預測
        df_test_predictions = automl.predict_all(df_test_X)
        df_test_predictions.to_csv(fp+"/"+ML_folder_name+"/"+test_df_filename[0:-4]+"_predict_propa.csv",index=False)

        df_test2_predictions = automl.predict_all(df_test2_X)
        df_test2_predictions.to_csv(fp+"/"+ML_folder_name+"/"+test_df_filename2[0:-4]+"_predict_propa.csv",index=False)
        
        df_test_predictions_file=str(fp+"/"+ML_folder_name+"/"+test_df_filename[0:-4]+"_predict_propa.csv")
        df_test2_predictions_file=str(fp+"/"+ML_folder_name+"/"+test_df_filename2[0:-4]+"_predict_propa.csv")
        if eval_metric=="rmse":
            df_test_eval_metric=mean_squared_error(df_test_y, df_test_predictions["label"].astype(int), squared=False)
            df_test2_eval_metric=mean_squared_error(df_test2_y, df_test2_predictions["label"].astype(int), squared=False)
            
        elif eval_metric=="mse":
            df_test_eval_metric=mean_squared_error(df_test_y, df_test_predictions["label"].astype(int))
            df_test2_eval_metric=mean_squared_error(df_test2_y, df_test2_predictions["label"].astype(int))
            
        elif eval_metric=="mae":
            df_test_eval_metric=mean_absolute_error(df_test_y, df_test_predictions["label"].astype(int))
            df_test2_eval_metric=mean_absolute_error(df_test2_y, df_test2_predictions["label"].astype(int))
            
        elif eval_metric=="r2":
            df_test_eval_metric=r2_score(df_test_y, df_test_predictions["label"].astype(int))
            df_test2_eval_metric=r2_score(df_test2_y, df_test2_predictions["label"].astype(int))
            
        elif eval_metric=="logloss":
            df_test_eval_metric=log_loss(df_test_y, df_test_predictions["label"].astype(int))
            df_test2_eval_metric=log_loss(df_test2_y, df_test2_predictions["label"].astype(int))
            
        elif eval_metric=="auc":
            df_test_eval_metric=roc_auc_score(df_test_y, df_test_predictions["prediction_1"])
            df_test2_eval_metric=roc_auc_score(df_test2_y, df_test2_predictions["prediction_1"])
            
        elif eval_metric=="f1":
            df_test_eval_metric=f1_score(df_test_y, df_test_predictions["label"].astype(int))
            df_test2_eval_metric=f1_score(df_test2_y, df_test2_predictions["label"].astype(int))
            
        elif eval_metric=="accuracy":
            df_test_eval_metric=accuracy_score(df_test_y, df_test_predictions["label"].astype(int))
            df_test2_eval_metric=accuracy_score(df_test2_y, df_test2_predictions["label"].astype(int))
        return render_template("page_after_Auto_ML.html",
        super_mission_type=super_mission_type,#因前端要依據任務類型不同回饋不同項目，故此處要有一個宣告
        name=name,model_type=model_type,metric_type=metric_type,metric_value=metric_value,train_time=train_time,#這行是輸出leaderboard資料用
        features_heatmap=features_heatmap,ldb_performance_boxplot=ldb_performance_boxplot,correlation_heatmap=correlation_heatmap,#這行是輸出總表類圖片用
        pic1=pic1,pic3=pic3,pic4=pic4, #最佳表現資料模型的圖片預覽
        validation_result=validation_result,#最佳模型預測validation資料集的或然率結果csv檔
        test_df_num=test_df_num,#宣告測試資料集數量給前端以利展示預測結果
        eval_metric=eval_metric,#回饋前端顯示評價指標名稱
        df_test_eval_metric=df_test_eval_metric,df_test2_eval_metric=df_test2_eval_metric,#221012增加測試資料集的預測結果的評價指標
        df_test_predictions_file=df_test_predictions_file,df_test2_predictions_file=df_test2_predictions_file,#221012增加下載測試資料集的預測結果檔案路徑
        )    
    elif test_df_filename!="不該存在的檔案": #假設只有一個測試資料集
        test_df_num=1
        df_test=pd.read_csv(test_df_folder_path+"/"+test_df_filename[0:-4]+"_after_preprocessing.csv")
        df_test_X=df_test.drop(label_column,axis=1)
        df_test_y=df_test[label_column]

        automl = AutoML(results_path=fp+"/"+ML_folder_name) #用模型預測
        df_test_predictions = automl.predict_all(df_test_X)
        df_test_predictions.to_csv(fp+"/"+ML_folder_name+"/"+test_df_filename[0:-4]+"_predict_propa.csv",index=False)
        df_test_predictions_file=str(fp+"/"+ML_folder_name+"/"+test_df_filename[0:-4]+"_predict_propa.csv")
        
        if eval_metric=="rmse":
            df_test_eval_metric=mean_squared_error(df_test_y, df_test_predictions["label"].astype(int), squared=False)
            
            
        elif eval_metric=="mse":
            df_test_eval_metric=mean_squared_error(df_test_y, df_test_predictions["label"].astype(int))
            
            
        elif eval_metric=="mae":
            df_test_eval_metric=mean_absolute_error(df_test_y, df_test_predictions["label"].astype(int))
            
            
        elif eval_metric=="r2":
            df_test_eval_metric=r2_score(df_test_y, df_test_predictions["label"].astype(int))
            
            
        elif eval_metric=="logloss":
            df_test_eval_metric=log_loss(df_test_y, df_test_predictions["label"].astype(int))
            
            
        elif eval_metric=="auc":
            df_test_eval_metric=roc_auc_score(df_test_y, df_test_predictions["prediction_1"])
            
            
        elif eval_metric=="f1":
            df_test_eval_metric=f1_score(df_test_y, df_test_predictions["label"].astype(int))
            
            
        elif eval_metric=="accuracy":
            df_test_eval_metric=accuracy_score(df_test_y, df_test_predictions["label"].astype(int))

        return render_template("page_after_Auto_ML.html",
        super_mission_type=super_mission_type,#因前端要依據任務類型不同回饋不同項目，故此處要有一個宣告
        name=name,model_type=model_type,metric_type=metric_type,metric_value=metric_value,train_time=train_time,#這行是輸出leaderboard資料用
        features_heatmap=features_heatmap,ldb_performance_boxplot=ldb_performance_boxplot,correlation_heatmap=correlation_heatmap,#這行是輸出總表類圖片用
        pic1=pic1,pic3=pic3,pic4=pic4, #最佳表現資料模型的圖片預覽
        validation_result=validation_result,#最佳模型預測validation資料集的或然率結果csv檔
        test_df_num=test_df_num,#宣告測試資料集數量給前端以利展示預測結果
        eval_metric=eval_metric,#回饋前端顯示評價指標名稱
        df_test_eval_metric=df_test_eval_metric,#221012增加測試資料集的預測結果的評價指標
        df_test_predictions_file=df_test_predictions_file,#221012增加下載測試資料集的預測結果檔案路徑
        )
    #====================================
    else:
        test_df_num=0
    return render_template("page_after_Auto_ML.html",
    super_mission_type=super_mission_type,#因前端要依據任務類型不同回饋不同項目，故此處要有一個宣告
    name=name,model_type=model_type,metric_type=metric_type,metric_value=metric_value,train_time=train_time,#這行是輸出leaderboard資料用
    features_heatmap=features_heatmap,ldb_performance_boxplot=ldb_performance_boxplot,correlation_heatmap=correlation_heatmap,#這行是輸出總表類圖片用
    pic1=pic1,pic3=pic3,pic4=pic4, #最佳表現資料模型的圖片預覽
    validation_result=validation_result,#最佳模型預測validation資料集的或然率結果csv檔
    test_df_num=test_df_num,#宣告測試資料集數量給前端以利展示預測結果
    )
        

@ML.route("/MLJAR_connect_explain",methods=["post"])#當使用者選定快速模式會跳轉至這裡
@login_required
def MLJAR_connect_explain():
    #讀取訓練資料集與分割XY
    fp=session["folder_path"]
    fn=session["filename"]
    ML_folder_name="AutoML"
    os.mkdir(fp+"/"+ML_folder_name)
    df=pd.read_csv(fp+"/"+fn[0:-4]+"_after_preprocessing.csv")
    label_column=session["label_column"]
    x=df.drop(label_column,axis=1)
    y=df[label_column]
    #開始抓取MLJAR需要參數
    super_mission_type=session["ml_task"]
    super_regression_eva=session["super_regression_eva"] #評價指標三者只會有一個存在，其餘為空值
    binary_class_eva=session["binary_class_eva"] #評價指標三者只會有一個存在，其餘為空值
    multi_class_eva=session["multi_class_eva"] #評價指標三者只會有一個存在，其餘為空值
    if super_regression_eva!="":
        eval_metric=super_regression_eva
    elif binary_class_eva!="":
        eval_metric=binary_class_eva
    elif multi_class_eva!="":
        eval_metric=multi_class_eva
    session["eval_metric"]=eval_metric
    #220927加入MLJAR段落
    automl = AutoML(
            results_path=fp+"/"+ML_folder_name,
            ml_task=super_mission_type,
            mode="Explain",
            explain_level=1,
            eval_metric=eval_metric,
            ) 
    automl.fit(x, y)

    #221003增加讀取leader_board.csv檔案
    lb=pd.read_csv(fp+"/"+ML_folder_name+"/leaderboard.csv")
    name=lb["name"].values.tolist()
    model_type=lb["model_type"].values.tolist()
    metric_type=lb["metric_type"].values.tolist()
    metric_value=lb["metric_value"].values.tolist()
    train_time=lb["train_time"].values.tolist()
    #221003增加以下總表類圖片顯示
    features_heatmap=str(fp+"/"+ML_folder_name+"/features_heatmap.png")#features_heatmap.png
    ldb_performance_boxplot=str(fp+"/"+ML_folder_name+"/ldb_performance_boxplot.png")
    correlation_heatmap=str(fp+"/"+ML_folder_name+"/correlation_heatmap.png")
    #221004新增最佳模型的資料輸出
    eval_metric=session["eval_metric"]
    if eval_metric!=["mae","rmse","logloss"]:
        sort_df = lb.nlargest(1, "metric_value").iloc[0] #會從leaderboard.csv中抓出表現越大的
    else:
        sort_df = lb.nsmallest(1, "metric_value").iloc[0] #會從leaderboard.csv中抓出表現最小的
    target_folder=str(fp+"/"+ML_folder_name+"/"+sort_df["name"])
    super_mission_type=session["ml_task"]
    if super_mission_type=="regression": #221004因回歸與分類任務顯示的圖片不同所以要分開
        pic1=str(target_folder+"/"+"permutation_importance.png")
        pic3=str(target_folder+"/"+"predicted_vs_residuals.png")
        pic4=str(target_folder+"/"+"true_vs_predicted.png")
    else:
        pic1=str(target_folder+"/"+"confusion_matrix.png")
        pic3=str(target_folder+"/"+"permutation_importance.png")
        pic4=str(target_folder+"/"+"roc_curve.png")
    validation_result=str(target_folder+"/"+"predictions_validation.csv")

    #======221011測試新增預測測試資料集======
    
    test_df_folder_path=session["test_df_folder_path"]
    test_df_filename=session["test_df_filename"]
    test_df_filename2=session["test_df_filename2"]
    test_df_filename3=session["test_df_filename3"]
    if test_df_filename3!="不該存在的檔案3":#假設使用者最多上傳三個測試資料集
        test_df_num=3
        df_test=pd.read_csv(test_df_folder_path+"/"+test_df_filename[0:-4]+"_after_preprocessing.csv")
        df_test_X=df_test.drop(label_column,axis=1)
        df_test_y=df_test[label_column]
        
        df_test2=pd.read_csv(test_df_folder_path+"/"+test_df_filename2[0:-4]+"_after_preprocessing.csv")
        df_test2_X=df_test2.drop(label_column,axis=1)
        df_test2_y=df_test2[label_column]

        df_test3=pd.read_csv(test_df_folder_path+"/"+test_df_filename3[0:-4]+"_after_preprocessing.csv")
        df_test3_X=df_test3.drop(label_column,axis=1)
        df_test3_y=df_test3[label_column]

        automl = AutoML(results_path=fp+"/"+ML_folder_name) #用模型預測
        df_test_predictions = automl.predict_all(df_test_X)
        df_test_predictions.to_csv(fp+"/"+ML_folder_name+"/"+test_df_filename[0:-4]+"_predict_propa.csv",index=False)
        
        df_test2_predictions = automl.predict_all(df_test2_X)
        df_test2_predictions.to_csv(fp+"/"+ML_folder_name+"/"+test_df_filename2[0:-4]+"_predict_propa.csv",index=False)
        
        df_test3_predictions = automl.predict_all(df_test3_X)
        df_test3_predictions.to_csv(fp+"/"+ML_folder_name+"/"+test_df_filename3[0:-4]+"_predict_propa.csv",index=False)
        
        df_test_predictions_file=str(fp+"/"+ML_folder_name+"/"+test_df_filename[0:-4]+"_predict_propa.csv")
        df_test2_predictions_file=str(fp+"/"+ML_folder_name+"/"+test_df_filename2[0:-4]+"_predict_propa.csv")
        df_test3_predictions_file=str(fp+"/"+ML_folder_name+"/"+test_df_filename3[0:-4]+"_predict_propa.csv")
        if eval_metric=="rmse":
            df_test_eval_metric=round(mean_squared_error(df_test_y, df_test_predictions["label"].astype(int), squared=False),2)
            df_test2_eval_metric=round(mean_squared_error(df_test2_y, df_test2_predictions["label"].astype(int), squared=False),2)
            df_test3_eval_metric=round(mean_squared_error(df_test3_y, df_test3_predictions["label"].astype(int), squared=False),2)
        elif eval_metric=="mse":
            df_test_eval_metric=round(mean_squared_error(df_test_y, df_test_predictions["label"].astype(int)),2)
            df_test2_eval_metric=round(mean_squared_error(df_test2_y, df_test2_predictions["label"].astype(int)),2)
            df_test3_eval_metric=round(mean_squared_error(df_test3_y, df_test3_predictions["label"].astype(int)),2)
        elif eval_metric=="mae":
            df_test_eval_metric=round(mean_absolute_error(df_test_y, df_test_predictions["label"].astype(int)),2)
            df_test2_eval_metric=round(mean_absolute_error(df_test2_y, df_test2_predictions["label"].astype(int)),2)
            df_test3_eval_metric=round(mean_absolute_error(df_test3_y, df_test3_predictions["label"].astype(int)),2)
        elif eval_metric=="r2":
            df_test_eval_metric=round(r2_score(df_test_y, df_test_predictions["label"].astype(int)),2)
            df_test2_eval_metric=round(r2_score(df_test2_y, df_test2_predictions["label"].astype(int)),2)
            df_test3_eval_metric=round(r2_score(df_test3_y, df_test3_predictions["label"].astype(int)),2)
        elif eval_metric=="logloss":
            df_test_eval_metric=round(log_loss(df_test_y, df_test_predictions["label"].astype(int)),2)
            df_test2_eval_metric=round(log_loss(df_test2_y, df_test2_predictions["label"].astype(int)),2)
            df_test3_eval_metric=round(log_loss(df_test3_y, df_test3_predictions["label"].astype(int)),2)
        elif eval_metric=="auc":
            df_test_eval_metric=round(roc_auc_score(df_test_y, df_test_predictions["prediction_1"]),2)
            df_test2_eval_metric=round(roc_auc_score(df_test2_y, df_test2_predictions["prediction_1"]),2)
            df_test3_eval_metric=round(roc_auc_score(df_test3_y, df_test3_predictions["prediction_1"]),2)
        elif eval_metric=="f1":
            df_test_eval_metric=round(f1_score(df_test_y, df_test_predictions["label"].astype(int)),2)
            df_test2_eval_metric=round(f1_score(df_test2_y, df_test2_predictions["label"].astype(int)),2)
            df_test3_eval_metric=round(f1_score(df_test3_y, df_test3_predictions["label"].astype(int)),2)
        elif eval_metric=="accuracy":
            df_test_eval_metric=round(accuracy_score(df_test_y, df_test_predictions["label"].astype(int)),2)
            df_test2_eval_metric=round(accuracy_score(df_test2_y, df_test2_predictions["label"].astype(int)),2)
            df_test3_eval_metric=round(accuracy_score(df_test3_y, df_test3_predictions["label"].astype(int)),2)
        return render_template("page_after_Auto_ML.html",
        super_mission_type=super_mission_type,#因前端要依據任務類型不同回饋不同項目，故此處要有一個宣告
        name=name,model_type=model_type,metric_type=metric_type,metric_value=metric_value,train_time=train_time,#這行是輸出leaderboard資料用
        features_heatmap=features_heatmap,ldb_performance_boxplot=ldb_performance_boxplot,correlation_heatmap=correlation_heatmap,#這行是輸出總表類圖片用
        pic1=pic1,pic3=pic3,pic4=pic4, #最佳表現資料模型的圖片預覽
        validation_result=validation_result,#最佳模型預測validation資料集的或然率結果csv檔
        test_df_num=test_df_num,#宣告測試資料集數量給前端以利展示預測結果
        eval_metric=eval_metric,#回饋前端顯示評價指標名稱
        df_test_eval_metric=df_test_eval_metric,df_test2_eval_metric=df_test2_eval_metric,df_test3_eval_metric=df_test3_eval_metric,#221012增加測試資料集的預測結果的評價指標
        df_test_predictions_file=df_test_predictions_file,df_test2_predictions_file=df_test2_predictions_file,df_test3_predictions_file=df_test3_predictions_file,#221012增加下載測試資料集的預測結果檔案路徑
        )
    elif test_df_filename2!="不該存在的檔案2": #假設使用者上傳兩個測試資料集
        test_df_num=2
        df_test=pd.read_csv(test_df_folder_path+"/"+test_df_filename[0:-4]+"_after_preprocessing.csv")
        df_test_X=df_test.drop(label_column,axis=1)
        df_test_y=df_test[label_column]

        df_test2=pd.read_csv(test_df_folder_path+"/"+test_df_filename2[0:-4]+"_after_preprocessing.csv")
        df_test2_X=df_test2.drop(label_column,axis=1)
        df_test2_y=df_test2[label_column]

        automl = AutoML(results_path=fp+"/"+ML_folder_name) #用模型預測
        df_test_predictions = automl.predict_all(df_test_X)
        df_test_predictions.to_csv(fp+"/"+ML_folder_name+"/"+test_df_filename[0:-4]+"_predict_propa.csv",index=False)

        df_test2_predictions = automl.predict_all(df_test2_X)
        df_test2_predictions.to_csv(fp+"/"+ML_folder_name+"/"+test_df_filename2[0:-4]+"_predict_propa.csv",index=False)
        
        df_test_predictions_file=str(fp+"/"+ML_folder_name+"/"+test_df_filename[0:-4]+"_predict_propa.csv")
        df_test2_predictions_file=str(fp+"/"+ML_folder_name+"/"+test_df_filename2[0:-4]+"_predict_propa.csv")
        if eval_metric=="rmse":
            df_test_eval_metric=round(mean_squared_error(df_test_y, df_test_predictions["label"].astype(int), squared=False),2)
            df_test2_eval_metric=round(mean_squared_error(df_test2_y, df_test2_predictions["label"].astype(int), squared=False),2)
            
        elif eval_metric=="mse":
            df_test_eval_metric=round(mean_squared_error(df_test_y, df_test_predictions["label"].astype(int)),2)
            df_test2_eval_metric=round(mean_squared_error(df_test2_y, df_test2_predictions["label"].astype(int)),2)
            
        elif eval_metric=="mae":
            df_test_eval_metric=round(mean_absolute_error(df_test_y, df_test_predictions["label"].astype(int)),2)
            df_test2_eval_metric=round(mean_absolute_error(df_test2_y, df_test2_predictions["label"].astype(int)),2)
            
        elif eval_metric=="r2":
            df_test_eval_metric=round(r2_score(df_test_y, df_test_predictions["label"].astype(int)),2)
            df_test2_eval_metric=round(r2_score(df_test2_y, df_test2_predictions["label"].astype(int)),2)
            
        elif eval_metric=="logloss":
            df_test_eval_metric=round(log_loss(df_test_y, df_test_predictions["label"].astype(int)),2)
            df_test2_eval_metric=round(log_loss(df_test2_y, df_test2_predictions["label"].astype(int)),2)
            
        elif eval_metric=="auc":
            df_test_eval_metric=round(roc_auc_score(df_test_y, df_test_predictions["prediction_1"]),2)
            df_test2_eval_metric=round(roc_auc_score(df_test2_y, df_test2_predictions["prediction_1"]),2)
            
        elif eval_metric=="f1":
            df_test_eval_metric=round(f1_score(df_test_y, df_test_predictions["label"].astype(int)),2)
            df_test2_eval_metric=round(f1_score(df_test2_y, df_test2_predictions["label"].astype(int)),2)
            
        elif eval_metric=="accuracy":
            df_test_eval_metric=round(accuracy_score(df_test_y, df_test_predictions["label"].astype(int)),2)
            df_test2_eval_metric=round(accuracy_score(df_test2_y, df_test2_predictions["label"].astype(int)),2)
        return render_template("page_after_Auto_ML.html",
        super_mission_type=super_mission_type,#因前端要依據任務類型不同回饋不同項目，故此處要有一個宣告
        name=name,model_type=model_type,metric_type=metric_type,metric_value=metric_value,train_time=train_time,#這行是輸出leaderboard資料用
        features_heatmap=features_heatmap,ldb_performance_boxplot=ldb_performance_boxplot,correlation_heatmap=correlation_heatmap,#這行是輸出總表類圖片用
        pic1=pic1,pic3=pic3,pic4=pic4, #最佳表現資料模型的圖片預覽
        validation_result=validation_result,#最佳模型預測validation資料集的或然率結果csv檔
        test_df_num=test_df_num,#宣告測試資料集數量給前端以利展示預測結果
        eval_metric=eval_metric,#回饋前端顯示評價指標名稱
        df_test_eval_metric=df_test_eval_metric,df_test2_eval_metric=df_test2_eval_metric,#221012增加測試資料集的預測結果的評價指標
        df_test_predictions_file=df_test_predictions_file,df_test2_predictions_file=df_test2_predictions_file,#221012增加下載測試資料集的預測結果檔案路徑
        )    
    elif test_df_filename!="不該存在的檔案": #假設只有一個測試資料集
        test_df_num=1
        df_test=pd.read_csv(test_df_folder_path+"/"+test_df_filename[0:-4]+"_after_preprocessing.csv")
        df_test_X=df_test.drop(label_column,axis=1)
        df_test_y=df_test[label_column]

        automl = AutoML(results_path=fp+"/"+ML_folder_name) #用模型預測
        df_test_predictions = automl.predict_all(df_test_X)
        df_test_predictions.to_csv(fp+"/"+ML_folder_name+"/"+test_df_filename[0:-4]+"_predict_propa.csv",index=False)
        df_test_predictions_file=str(fp+"/"+ML_folder_name+"/"+test_df_filename[0:-4]+"_predict_propa.csv")
        
        if eval_metric=="rmse":
            df_test_eval_metric=round(mean_squared_error(df_test_y, df_test_predictions["label"].astype(int), squared=False),2)
            
            
        elif eval_metric=="mse":
            df_test_eval_metric=round(mean_squared_error(df_test_y, df_test_predictions["label"].astype(int)),2)
            
            
        elif eval_metric=="mae":
            df_test_eval_metric=round(mean_absolute_error(df_test_y, df_test_predictions["label"].astype(int)),2)
            
            
        elif eval_metric=="r2":
            df_test_eval_metric=round(r2_score(df_test_y, df_test_predictions["label"].astype(int)),2)
            
            
        elif eval_metric=="logloss":
            df_test_eval_metric=round(log_loss(df_test_y, df_test_predictions["label"].astype(int)),2)
            
            
        elif eval_metric=="auc":
            df_test_eval_metric=round(roc_auc_score(df_test_y, df_test_predictions["prediction_1"]),2)
            
            
        elif eval_metric=="f1":
            df_test_eval_metric=round(f1_score(df_test_y, df_test_predictions["label"].astype(int)),2)
            
            
        elif eval_metric=="accuracy":
            df_test_eval_metric=round(accuracy_score(df_test_y, df_test_predictions["label"].astype(int)),2)

        return render_template("page_after_Auto_ML.html",
        super_mission_type=super_mission_type,#因前端要依據任務類型不同回饋不同項目，故此處要有一個宣告
        name=name,model_type=model_type,metric_type=metric_type,metric_value=metric_value,train_time=train_time,#這行是輸出leaderboard資料用
        features_heatmap=features_heatmap,ldb_performance_boxplot=ldb_performance_boxplot,correlation_heatmap=correlation_heatmap,#這行是輸出總表類圖片用
        pic1=pic1,pic3=pic3,pic4=pic4, #最佳表現資料模型的圖片預覽
        validation_result=validation_result,#最佳模型預測validation資料集的或然率結果csv檔
        test_df_num=test_df_num,#宣告測試資料集數量給前端以利展示預測結果
        eval_metric=eval_metric,#回饋前端顯示評價指標名稱
        df_test_eval_metric=df_test_eval_metric,#221012增加測試資料集的預測結果的評價指標
        df_test_predictions_file=df_test_predictions_file,#221012增加下載測試資料集的預測結果檔案路徑
        )
    #====================================
    else:
        test_df_num=0
    return render_template("page_after_Auto_ML.html",
    super_mission_type=super_mission_type,#因前端要依據任務類型不同回饋不同項目，故此處要有一個宣告
    name=name,model_type=model_type,metric_type=metric_type,metric_value=metric_value,train_time=train_time,#這行是輸出leaderboard資料用
    features_heatmap=features_heatmap,ldb_performance_boxplot=ldb_performance_boxplot,correlation_heatmap=correlation_heatmap,#這行是輸出總表類圖片用
    pic1=pic1,pic3=pic3,pic4=pic4, #最佳表現資料模型的圖片預覽
    validation_result=validation_result,#最佳模型預測validation資料集的或然率結果csv檔
    test_df_num=test_df_num,#宣告測試資料集數量給前端以利展示預測結果
    )
#221004新增下載最佳模型功能
@ML.route("/download_best_model",methods=["post","get"])
@login_required
def download_best_model():
    fp=session["folder_path"]
    ML_folder_name="AutoML"
    file_path = os.path.join(fp+"/"+ML_folder_name+"/leaderboard.csv")
    lb = pd.read_csv(file_path)#先讀取leaderboard.csv
    output_file = str(fp+"/"+ML_folder_name+"/Best_model_data.zip") # 指定輸出的壓縮檔名和路徑
    tar_folder=str(fp+"/"+ML_folder_name)#輸出壓縮檔的路徑
    eval_metric=session["eval_metric"]
    if eval_metric!=["mae","mape","rmse","logloss"]:#221004加一個判定依據評價指標不同可能要抓最大或最小值
        sort_df = lb.nlargest(1, "metric_value").iloc[0] #會從leaderboard.csv中抓出表現越大的
    else:
        sort_df = lb.nsmallest(1, "metric_value").iloc[0] #會從leaderboard.csv中抓出表現最小的
    # print(sort_df)

    #以下是將最佳模型的資料夾壓縮的語法
    zip_file = zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED)  # 建立一個.zip檔案
    for path, folders, files in os.walk(tar_folder+"/" +sort_df["name"]):  # 遍歷指定壓縮路徑，獲得其目錄結構
        #print("folders: ",folders) #空的
        
        new_path = path.replace(tar_folder, '')  # 將指定壓縮路徑替換為空，以得到其內部檔案和資料夾的相對路徑
        #print(new_path) #/6_Default_RandomForest
        for filename in files:  # 遍歷某一層級資料夾內所有檔案
            zip_file.write(os.path.join(path, filename), os.path.join(new_path, filename))  # 向壓縮檔案內新增檔案

    zip_file.write(r"static/file_explaination/README.docx",basename(r"static/file_explaination/README.docx"))#221014新增可打包的檔案說明word
    zip_file.close()  # 對目標.zip檔案操作完畢，關閉操作物件
    download_file=output_file

    return send_file(download_file,as_attachment=True)

#221004新增下載總表類圖片功能
@ML.route("/download_summary_files",methods=["post","get"])
@login_required
def download_summary_files():
    fp=session["folder_path"]
    ML_folder_name="AutoML"
    source_folder=str(fp+"/"+ML_folder_name)
    print("source_folder: ",source_folder)
    output_file = str("Summary_files.zip") # 指定輸出的壓縮檔名和路徑
    zip_file = zipfile.ZipFile(source_folder+"/"+output_file, "w", zipfile.ZIP_DEFLATED)  # 建立一個.zip檔案
    for file in os.listdir(source_folder):
        if ".png" in file:
            zip_file.write(os.path.join(source_folder,file),basename(os.path.join(output_file, file)))  # 向壓縮檔案內新增檔案
        elif "leaderboard.csv" in file:
            zip_file.write(os.path.join(source_folder,file),basename(os.path.join(output_file, file)))  # 向壓縮檔案內新增檔案
    zip_file.write(r"static/file_explaination/README.docx",basename(r"static/file_explaination/README.docx"))#221014新增可打包的檔案說明word
    zip_file.close()  # 對目標.zip檔案操作完畢，關閉操作物件
    download_pic=str(source_folder+"/"+output_file)
    return send_file(download_pic,as_attachment=True)


