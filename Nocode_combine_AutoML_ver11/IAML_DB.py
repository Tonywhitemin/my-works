from flask import Flask
from flask import session
from flask import Blueprint
from flask import request
from flask import render_template
from flask import redirect
from flask import session
import os
from pymongo import MongoClient #mongoDB
from email.mime.text import MIMEText
import function_send_mail
from function_login_requirement import login_required


DB= Blueprint("DB",__name__)


#=====
# 連接到本地 MongoDB 伺服器
client = MongoClient()

# 選擇要使用的資料庫
db = client['IAML_members']

# 選擇要使用的集合（資料表）
collection = db['member_list']
#=====


#230606註冊成功後的登入頁面
@DB.route('/success_registed',methods=["POST","GET"])
def success_registed():
    return render_template("Log_in_after_register.html")

#230606登入時密碼輸入錯誤顯示頁面
@DB.route('/password_wrong',methods=["GET"])
def password_wrong():
    return render_template("Log_in_but_wrong_password.html")

#230606登入時帳號輸入錯誤顯示頁面
@DB.route('/account_wrong',methods=["GET"])
def account_wrong():
    return render_template("Log_in_but_wrong_account.html")

#230608忘記密碼時要寄送訊息
@DB.route('/forget_password',methods=["GET"])
def forget_password():
    return render_template("forget_password.html")

#230608忘記密碼後端接收前端使用者傳送的信箱資訊
@DB.route('/send_email',methods=["POST"])
def send_email():
    email_check=request.values["email_check"]
    # =====查詢特定一筆資料=====
    query = {'email': email_check}
    result = collection.find_one(query)
    if result!=None:
        from_mail = {'name': "IAML管理者", 'addr': 'tonywhitemin@gmail.com'}  # 寄信者
        to_mail = {'name': result["username"], 'addr': result["email"]}  # 收信者
        to_message ='您的IAML平台帳號密碼如下：\n'+result["account"]+"\n"+ result["password"] # 信件標題  # 信件內容
        text = MIMEText(to_message, 'plain', 'utf-8')
        text['Subject'] = "您的IAML平台帳號密碼"
        text['From'] = from_mail['name']  # 寄信者
        text['To'] = to_mail['name']  # 收信者
        text = text.as_string()
        function_send_mail.send_email(from_mail['addr'], to_mail['addr'], text)
        return render_template("Log_in_after_mailed_password.html")
    else:
        return render_template("forget_password_but_no_email.html")
    

#230606帳號密碼確認
@DB.route('/sign_in_check',methods=["POST"])
def sign_in_check():
    account=request.values["account"]
    password=request.values["password"]   

    # =====查詢資料庫中指定一筆資料=====
    query = {'account': account}
    result = collection.find_one(query)
    if result!=None:
        print("密碼為：",result["password"])
        if result["password"]==password:
            session["user_id"]=account #這行是給避免其他使用者透過直接修改路由直接跳到其他頁面
            session["user_account_folder"]=account
            return redirect("homepage")
        else:
            return redirect("password_wrong")
    else:
        return redirect("account_wrong")



#230606以下為註冊頁面
@DB.route('/register',methods=["POST","GET"])
def register():
    return render_template("register.html") 

#230606以下為註冊帳號重複時的重新導向
@DB.route('/register-error',methods=["POST","GET"])
def register_error():
    return render_template("register-error.html") 

# 230606這頁為後端接收使用者提交的註冊資料
# @DB.route('/user_sign_up',methods=["POST"])
@DB.route('/user_sign_up',methods=["POST"])
def user_sign_up():
    username=request.values["username"]
    email=request.values["email"]
    department=request.values["department"]
    account=request.values["account"]
    password=request.values["password"]
    password_double_check=request.values["password_double_check"]
    if password!=password_double_check:
        return render_template("register_password_wrong.html")
    
    query = {'account': str(account)}
    existing_document = collection.find_one(query)

    if existing_document:
        print('已存在相同的文件:', existing_document)
        return redirect("register-error")
    else:
        # 插入一個文件
        document = {
            'username': username,
            'email': email,
            'department': department,
            'account': account,
            'password': password,
        }
        result = collection.insert_one(document)
        UPLOAD_FOLDER = r'static/tmp'
        user_folder_path=os.path.join(UPLOAD_FOLDER,account)
        os.mkdir(user_folder_path)
        session["user_account_folder"]=account
        
    return redirect("success_registed")
    



