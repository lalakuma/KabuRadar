import requests
from datetime import datetime

# 取得したチャネルアクセストークンをここに入れる
CHANNEL_ACCESS_TOKEN = "gEi4Q43g1Ea6VPvORh6A1GDJPVvAYXu1xW3ET+3snd9WHO/rWJK25UVdha2wwi/hRQot1dsuhTc1JeJtiLCZDgGkNlzX73iK4EFCylYvKaOlrQn1xKyqNA5qU+HRqYaESzRveo9k4LnjU/ZmvJrZ4wdB04t89/1O/w1cDnyilFU="

# 送信先ユーザーID（LINEのユーザーID）
USER_IDS = ["U3e137aee8d1c0c0dc357776f6f545f31","Ua14a85e0c4616d087ea0159554b326f4"]

def line_notify(lst_codes, stance):
    # 土曜日（7）と日曜日（6）は通知を送らない
    iWeek = datetime.today().isoweekday()
    if iWeek in [6, 7]:  
        print("今日は通知を送りません")
        return  

    # 送信するメッセージ作成
    message = "\n".join(lst_codes) if lst_codes else "not found"
    full_message = f"{stance} {message}"

    # LINE Messaging API のエンドポイント
    url = "https://api.line.me/v2/bot/message/multicast"

    # ヘッダー情報
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # 送信するデータ
    data = {
        "to": USER_IDS,
        "messages": [{"type": "text", "text": full_message}]
    }

    # APIリクエストを送信
    response = requests.post(url, headers=headers, json=data)

    # 結果を確認
    if response.status_code == 200:
        print("メッセージ送信成功！")
    else:
        print(f"エラー発生: {response.status_code} - {response.text}")

