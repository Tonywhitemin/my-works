
from email.mime.text import MIMEText
import smtplib


def send_email(frommail, tomail, text):
    smtp_server = 'smtp.gmail.com'  # Gmail Hostname
    smtp_server_port = 587  # Gmail Server Port
    smtp_server_account = 123456789@gmail.com'  # Gmail Account Name
    smtp_server_password = '3213t23y2y'  #230608 Gmail 應用程式密碼，不是一般登入信箱的密碼喔
    #應用程式密碼可參考：https://myaccount.google.com/apppasswords
    server = smtplib.SMTP(smtp_server, smtp_server_port)  # setting SMTP Server
    server.starttls()  # 信件加密
    server.login(smtp_server_account, smtp_server_password)  # 登入Gmail
    status = server.sendmail(frommail, tomail, text)  # 輸入信件內容
    if not status:
        print('寄信成功')
    else:
        print(f'寄信失敗。 {status}')
    server.quit()


