import cv2
import time
import sqlite3 as s3

model=cv2.face.LBPHFaceRecognizer_create()
model.read("Member_faces_LBPH.yml") #載入訓練完成的模型


conn = s3.connect("Members.db")  # 連結Members.db的資料庫
c = conn.cursor()
c.execute("SELECT * From Member") #讀取範圍為整個資料庫，ORDER BY id DESC表示倒數
items=c.fetchall()
conn.commit()  # 運行資料庫語法
conn.close()

face_cascade=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_alt2.xml")
cap=cv2.VideoCapture(0)
cv2.namedWindow("frame",cv2.WINDOW_NORMAL)

timenow=time.time() #取得現在時間數值作為倒數計時的起始時間
while(cap.isOpened()):#cam開啟成功
    count=2-int(time.time()-timenow) #2減掉目前經過的時間就是倒數計時時間
    ret,img=cap.read()
    if ret==True:
        frame=cv2.flip(img,1) #因為攝像頭左右會顛倒所以要轉置,1為水平翻轉，0為垂直翻轉
        imgcopy=frame.copy() #複製影像
        cv2.putText(imgcopy,str(count),(200,400),cv2.FONT_HERSHEY_SIMPLEX,15,(0,0,255),35)#在複製影像上倒數秒數
        cv2.imshow("frame",imgcopy) #顯示複製影像
        k=cv2.waitKey(100) #每0.1秒讀鍵盤一次看有沒有輸入
        if k==ord("z") or k==ord("Z") or count==0: #按Z鍵或倒數計時結束
            cv2.imwrite("media/tem.jpg",img) #將影像存檔
            break
cap.release()
cv2.destroyAllWindows()

img=cv2.imread("media/tem.jpg") #取得使用者圖片
gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) #進行臉部偵測
faces=face_cascade.detectMultiScale(gray,1.1,3)
for (x,y,w,h) in faces:
    img=cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),3) #框取人臉
    face_img=cv2.resize(gray[y:y+h,x:x+w],(400,400))#調整成訓練時的大小
    try:
        val=model.predict(face_img) #開始進行臉部辨識
        if val[1]<50: #辨識差異度val[1]<50表示辨識成功，顯示登入訊息
            for i in range(len(items)):              
                if val[0]==items[i][0]:
                    print("ID值為:", val[0])
                    print("歡迎"+items[i][1]+"登入!",val[1]) #由圖片索引[val[0]]取得會員姓名並顯示登入成功訊息
        else:
            print("抱歉!你不是會員，無法登入")
    except:
        print("辨識時發生錯誤")