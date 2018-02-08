# -*- coding:utf-8 -*-
# version 1.3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sendEmail import send_email
from configparser import ConfigParser

import os
import time
import sys
import pickle

class trainTickets:
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.loadConfig()

    def loadConfig(self):
        cp = ConfigParser()
        try:
            cp.read("config.ini", encoding="utf-8-sig")
        except IOError as e:
            print("配置文件config.ini打开失败, 请重新创建")
            input("Press any key to continue")
            sys.exit()
        # 用户名
        self.username = cp["login"]["username"]
        # 密码
        self.password = cp["login"]["password"]
        # 始发站
        from_station = cp["train_info"]["from_station"]
        # 将中文地点进行编码
        self.leave = self.convert_station(from_station)
        # 终点站
        to_station = cp["train_info"]["to_station"]
        self.arrive = self.convert_station(to_station)
        # 乘车时间
        self.leave_date = cp["train_info"]["from_date"]

    def convert_station(self, station):
        # 只读二进制方式打开station.pkl文件，读取二进制形式到station_file文件中
        station_file = open("station.pkl", "rb")
        # 使用pickle加载二进制文件station_file，到字典station_lists中
        station_lists = pickle.load(station_file)
        # 关闭文件
        station_file.close()

        station_unicode = station.encode("unicode_escape").decode("utf-8") \
                                 .replace("\\u", "%u")+"%2c"+station_lists[station]

        return station_unicode

  
    def login(self):
        login_url = "https://kyfw.12306.cn/otn/login/init"
        login_done_url = "https://kyfw.12306.cn/otn/index/initMy12306"
        self.browser.get(login_url)

        user = self.browser.find_element_by_id("username")  # 找到用户名输入框
        user.clear  # 清除用户名输入框内容
        user.send_keys(self.username)  # 在框中输入用户名

        pwd = self.browser.find_element_by_id("password")  # 找到密码输入框
        pwd.clear
        pwd.send_keys(self.password)

        while True:
            current_page_url = self.browser.current_url   # 获取当前页面url
            if current_page_url != login_url:
                if current_page_url[:-1] != login_url:  # 排除错误验证码页面
                    if current_page_url == login_done_url:  # 跳转成功
                        break
                else:
                    time.sleep(1)
                    print("自行点击，进行图片验证")

    def reserveTicket(self):
        reserve_url = "https://kyfw.12306.cn/otn/leftTicket/init"
        self.browser.get(reserve_url)

        self.browser.add_cookie({"name": "_jc_save_fromStation",
                                 "value": self.leave
                                 })

        self.browser.add_cookie({"name": "_jc_save_toStation",
                                 "value": self.arrive
                                 })

        self.browser.add_cookie({"name": "_jc_save_fromDate",
                                 "value": self.leave_date
                                 })
        self.browser.refresh()
        # browser.find_element_by_xpath("/html/body/div[5]/div[5]/div[2]/div[2]/div[2]/ul/li[2]/label")
        self.browser.find_element_by_xpath('//input[@name="cc_type" and @value="Z"]').click()

        self.browser.find_element_by_id("query_ticket").click()
        
    def queryTicket(self):
        print("you are booking")
        query_times = 0
        while True:
            time.sleep(0.1)
            time_begin = time.time()
            try:
                ticket = WebDriverWait(self.browser, 30).until(
                         EC.presence_of_element_located((By.XPATH, '//*[@id="RW_2400000Z630C"]'))
                         )
                ticket_status = ticket.text
            except:
                ticket = WebDriverWait(self.browser, 15).until(
                         EC.presence_of_element_located((By.XPATH, '//*[@id="RW_2400000Z630C"]'))
                         )
                ticket_status = ticket.text

            if ticket_status == "无" or ticket_status == "*":
                query_times += 1
                time_end = time.time()
                print("第{}次查询，此次耗时为{:.3}秒".format(query_times, time_end-time_begin))
                continue
            else:
                self.browser.find_element_by_xpath('//*[@id="ticket_2400000Z630C"]/td[13]/a').click()
                break

    def selectPassenger(self):
        passenger_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        while True:
            if self.browser.current_url == passenger_url:
                print("进入选择乘客信息界面")
                break
            else:
                print("等待页面跳转")

        while True:
            try:
                self.browser.find_element_by_xpath('//*[@id="normalPassenger_0"]').click()
                break
            except:
                print("等待刷新联系人列表")

        self.browser.find_element_by_xpath('//*[@id="submitOrder_id"]').click()

    def submitTicket(self):
        while True:
            try:
                self.browser.find_element_by_id("qr_submit_id").click()
                print("预定成功，请及时支付！")
                send_email()
                break
            except:
                print ("请手动通过图片验证码")
                time.sleep(3)
                break
            return "Welcome to back home!"

    def main(self):
        # 进入登录界面
        self.login()
        # 车票预订
        self.reserveTicket()
        # 车票查询
        self.queryTicket()
        # 选择乘客
        self.selectPassenger()
        # 提交订单
        self.submitTicket()


if __name__ == "__main__":
    trainTickets = trainTickets()
    trainTickets.main()

  # browser = login()
  # query(browser)
  # query_ticket(browser)
  # select_passenger(browser)
  # submit_ticket(browser)







