# -*- coding:utf-8 -*-
# version 1.0

"""
Function:
    If book tickets successfully,then send an email to notice you!
"""

import smtplib
from email.header import Header
from email.mime.text import MIMEText

mail_host = "smtp.163.com"      # SMTP服务器
mail_user = "xxx@163.com"       # 用户名
mail_pass = "xxx"               # 授权密码（非登录密码）

sender = "xxx@163.com"    # 发件人邮箱
receivers = "xxx@qq.com"  # 接收邮件

content = "您已成功预定车票，请及时支付完成订单！"     # 邮件内容
title = "12306订票通知"  # 邮件主题

def send_email():

    message = MIMEText(content, "plain", "utf-8")  # 内容, 格式, 编码
    message["From"] = "{}".format(sender)
    message["To"] = ",".join(receivers)
    message["Subject"] = title

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)



