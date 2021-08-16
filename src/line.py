#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

def line_notify(lst_codes):
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