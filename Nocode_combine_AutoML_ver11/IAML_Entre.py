from flask import Flask #載入FLASK
from flask import session
from IAML_preprocessing import df_pre
from IAML_machine_learning import ML
from IAML_DB import DB
from IAML_upload_file import Upload_file
from flask import render_template



app = Flask(__name__)
app.register_blueprint(df_pre)
app.register_blueprint(ML)
app.register_blueprint(Upload_file)
app.register_blueprint(DB)
# UPLOAD_FOLDER = r'static/tmp' #上傳檔案到路徑
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key="tttttiiiiii" #session套件必要的指令，但內容可以隨意取




#230606登入頁面
@app.route('/',methods=["GET"])
def db_homepage_login():
    if "user_id" in session:
        session.pop("user_id", None)
    return render_template("Log_in_page.html") 

if __name__ == '__main__':
    app.run(debug=True)