#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from datetime import datetime
import locale

def line_notify(lst_codes):

    # 土曜日と日曜日は通知処理を行わない
    iWeek = datetime.today().isoweekday()
    if iWeek == 6 or iWeek == 7:            #土日は終了 
        return

    url = "https://notify-api.line.me/api/notify" 
    token = "tcljLIH28mrzw0c2eEm4ff0KxxI2huuLZ8gMK58jol1"
    headers = {"Authorization" : "Bearer "+ token} 

    # 送信文字列作成
    message = ""
    for code in lst_codes:
        message += "\n" + code

    # リストにデータがなかった場合の処理
    if message == "":
        message = "not found"

    # LINEに通知する
    payload = {"message" :  message} 
    r = requests.post(url, headers = headers, params=payload) 
