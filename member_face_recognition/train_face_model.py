import cv2
import os,glob
import numpy as np
from time import sleep
import sqlite3 as s3
import re

name=input("輸入姓名(英文): ")
id=input("輸入五碼純數字ID: ")

check=re.match("[^a-zA-Z_%$#]{5}",id)
if not check:
    print("格式錯誤，請輸入'5'碼數字")
    quit()
elif len(id)>5:
    print("字元過長，請輸入'5'碼數字")
    quit()
#===================資料庫建立=====================
def database_setup():
    conn = s3.connect("Members.db")  # 與Members.db的資料庫連線，若沒有該檔案則會自動建立

    c = conn.cursor() #開始連結該檔案(cursor的意義可參考5.關於python與sql資料庫連結語法網路資料閱讀(自己找的)圖解)

    #以下為建立資料庫的欄位，注意引號(可用單引號或三引號皆可，但業界可能習慣用三引號因為若有跨多行時三引號較好用)
    c.execute(f""" CREATE TABLE Member(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, 
            member_name text
            )""")
    print("建立成功,開啟攝像頭準備拍攝100張照片做訓練，請看向鏡頭並維持20秒")
    conn.commit()  # 運行資料庫語法，提交也就是資料上傳
    conn.close()  # 關閉資料庫連結
set_db_check=input("是否要建立資料庫?(Y/N)")
if set_db_check=="Y":
    if os.path.isfile("Members.db"):#使用姓名作為資料夾名稱
        print("此檔案已存在，暫不覆蓋檔案，程式中止")
        quit()
    else:
        database_setup()
elif set_db_check!="Y":
    print("開啟攝像頭準備拍攝100張照片做訓練，請看向鏡頭並維持20秒")
#===================資料庫建立完成=====================

def saveImg(image,index):  #以下三行:儲存圖片的自訂函式,image參數為圖片，index參數為檔名流水號
    filename="images/"+id+name+"/face{:03d}.jpg".format(index) #設定圖片檔案名稱用自動產生方式，流水號有3碼
    cv2.imwrite(filename,image) #儲存檔案

index=1
total=100#人臉取樣總數



#=======資料庫新增資料=========
conn = s3.connect("Members.db")  # 連結customer.db的資料庫(上面一段已經建立該檔案故此處為連結)
c = conn.cursor()
c.execute(f"INSERT INTO Member values('{id}','{name}')") 
conn.commit()  # 運行資料庫語法
conn.close()  # 關閉資料庫連結

#=======以下為拍照與擷取圖片=========

if os.path.isdir("images/"+id+name):#使用姓名作為資料夾名稱
    print("該人員資料夾已存在")
else:
    os.mkdir("images/"+id+name) #建立資料夾
    face_cascade=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_alt2.xml")#haarcascade_frontalface_alt2.xml經測試準度較高所以用這個
    cap=cv2.VideoCapture(0) #開啟攝影機，0為內建的攝影機
    cv2.namedWindow("video",cv2.WINDOW_NORMAL) #建立一個視窗顯示影像
    while index>0: #此段為取樣100張人臉的迴圈
        ret,frame=cap.read() #讀取攝像頭畫面，ret為布林值變數，若為TRUE表示讀取影像成功，讀取成功得影像存於frame變數中
        frame=cv2.flip(frame,1) #因為攝像頭左右會顛倒所以要轉置,1為水平翻轉，0為垂直翻轉
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) #擷取灰階圖片(壓縮檔案)
        faces=face_cascade.detectMultiScale(gray,1.1,3) #偵測人臉，1.1是scalefactor，3是minneighbor
        for (x,y,w,h) in faces: #此段目的為逐張擷取人臉並存檔
            frame=cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3) #框選臉部，取得人臉圖型
            image=cv2.resize(gray[y:y+h,x:x+w],(400,400)) #存檔圖片大小為400X400固定尺寸
            saveImg(image,index)#與第43行的def呼應
            sleep(0.1) #暫停0.1秒，拉長擷取時間以利增加準確度與多樣化照片
            index+=1 #流水號+1
            if index>total: #若達到100張就結束取樣
                print("取樣完成!")
                index=-1 #離開迴圈
                break
        cv2.imshow("video",frame)
        cv2.waitKey(1)
    cap.release() #關閉攝像頭
    cv2.destroyAllWindows()

#======以下開始做模型訓練前處理=====
images=[] #存所有訓練圖型
labels=[] #存所有訓練標籤
count=0 #會員編號索引，以便加入labels串列中

conn = s3.connect("Members.db")  # 連結Members.db的資料庫(上面一段已經建立該檔案故此處為連結)
c = conn.cursor()
c.execute("SELECT id From Member") #讀取範圍為整個資料庫
items=c.fetchall()
conn.commit()  # 運行資料庫語法

dirs=os.listdir("images") #取得所有資料夾與檔案
for d in dirs: #逐一處理所有的資料夾與檔案
    if os.path.isdir("images/"+d): #只處理資料夾，如果是資料夾才執行以下
        print("抓的資料夾名稱為:",d)
        files=glob.glob("images/"+d+"/*.jpg") #取得資料夾中所有圖檔，讀取會員姓名資料夾中所有圖片檔案
        for filename in files: #逐一將會員姓名資料夾中圖片檔案加入圖片串列及標籤串列
            img=cv2.imread(filename,cv2.COLOR_BGR2GRAY)#讀取圖片且轉為灰階
            images.append(img)#對應89行
            pre_work=str(items[count])#對應資料庫最新一筆的id名稱
            pre_work1=int(pre_work[1:6])#從字串擷取第1-5字元為id名稱
            labels.append(pre_work1) #以id作為標籤
        print("存檔的ID為: ",pre_work1)
        count+=1 #會員索引+1

#========開始建立模型==========

print("開始建立模型...")
model=cv2.face.LBPHFaceRecognizer_create() #建立LBPH空模型
model.train(np.asarray(images),np.asarray(labels)) #訓練模型
model.save("Member_faces_LBPH.yml") #儲存訓練後的模型
print("建立模型完成")
# print(labels)
#pip install opencv-contrib-python注意版本

