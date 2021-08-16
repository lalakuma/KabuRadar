import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from pandas_datareader import data
 
 
####################################################
#   https://kabuoji3.com/から株価データを取得する
####################################################
def get_price_from_kabuoji3(ticker):    
    
    # URLを定義
    base_url = "https://kabuoji3.com/stock/{}/"
    url = base_url.format(ticker)
 
    # headersの設定     << "Chrome/91.0.4472.77"はユーザの環境毎に異なるらしい >>
    headers = {"User-Agent": "Chrome/91.0.4472.77"}
    
    # HTML取得
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    
    # 株価データ抽出
    rows = []
    
    for tr in soup.findAll("tr"):
        # thあればコラム、なければ株価データ
        if tr.find("th"):
            columns = [x.getText().strip() for x in tr.findAll("th")]
        else:
            rows.append([x.getText().strip() for x in tr.findAll("td")])
    
    # DataFrameに変換
    df_latest = pd.DataFrame(rows, columns=columns)
    
    # 日付をdatetimeに変換
    df_latest["日付"] = df_latest["日付"].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))
    
    # 日付以外のデータをfloatに変換
    for col in ["始値", "高値", "安値", "終値", "出来高", "終値調整"]:
        df_latest[col] = df_latest[col].astype(float)
    
    # "終値調整"を削除して返す
    return df_latest.drop("終値調整", axis=1)
 
 
def kabuoji_main(ticker):
    # https://kabuoji3.com/ からデータを取得する
    df_latest = get_price_from_kabuoji3(ticker)
 
    # pandas_datareaderから株価データを取得する
    df_past = data.DataReader('{}.JP'.format(ticker), 'stooq')
 
    # indexがDateになっているのでリセットする
    df_past.reset_index(inplace=True)
 
    # カラム名を合わせる
    df_past.columns = df_latest.columns
 
    # df_pastより新しいデータを抽出して結合する
    df = pd.concat([df_latest[df_latest["日付"]>df_past["日付"].max()], df_past])
 
    # 日付でソートする
    df.sort_values(by="日付", inplace=True)
 
    # indexをリセット
    df.reset_index(inplace=True, drop=True)
 
    return df
