import sqlite3
import pandas as pd
import datetime
from scipy.signal import find_peaks
import numpy as np
import sqlight as db
import os
import requests

import requests
import datetime

# Messaging API用のチャネルアクセストークン（ロングターム）
CHANNEL_ACCESS_TOKEN = "gEi4Q43g1Ea6VPvORh6A1GDJPVvAYXu1xW3ET+3snd9WHO/rWJK25UVdha2wwi/hRQot1dsuhTc1JeJtiLCZDgGkNlzX73iK4EFCylYvKaOlrQn1xKyqNA5qU+HRqYaESzRveo9k4LnjU/ZmvJrZ4wdB04t89/1O/w1cDnyilFU="

# 送信先ユーザーID（リスト形式で！）
USER_IDS = ["U3e137aee8d1c0c0dc357776f6f545f31","Ua14a85e0c4616d087ea0159554b326f4"]

def line_notify(results, stance="買いシグナル"):
    """LINE通知を送る関数（Messaging API対応）"""

    # 土曜日（6）・日曜日（7）は通知しない
    iWeek = datetime.date.today().isoweekday()
    if iWeek in [6,7]:
        print("週末のためLINE通知をスキップ")
        return

    # メッセージ作成（元の形式と同じ）
    message = ""
    for code, current_date, current_price, rim_date, rim_price in results:
        message += f"\n銘柄: {code} | {current_date.date()} | {current_price}円 | リム: {rim_price}円 ({rim_date.date()})"

    # 買いシグナルがない場合
    if not message:
        message = "本日付近（5日以内）に買いシグナルはありません。"

    # 完全メッセージ
    full_message = f"{stance}\n{message}"

    # Messaging APIの送信設定
    url = "https://api.line.me/v2/bot/message/multicast"
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": USER_IDS,
        "messages": [{"type": "text", "text": full_message}]
    }

    # POSTリクエスト送信
    response = requests.post(url, headers=headers, json=data)

    # レスポンス確認
    if response.status_code == 200:
        print("メッセージ送信成功！")
    else:
        print(f"エラー発生: {response.status_code} - {response.text}")

# --- 1. 定数定義（パラメータ調整可能） ---
PEAK_DISTANCE = 10              # 局所最小値（谷）を検出する際の最小間隔（日数）
PEAK_PROMINENCE_FACTOR = 0.25   # 局所最小値の「目立ち度」（標準偏差の倍率）
TOLERANCE = 0.03                # 買いシグナル判定時の価格許容範囲（3%）
LOOKBACK_WINDOW = 20            # 過去に遡る期間（直近20日間を分析）
DROP_THRESHOLD = 0.05           # 「深いカップ」の判定閾値（5%以上の下落）

# --- 2. DB接続 ---
conn, cursor = db.connect_db()

# --- 3. tbl_code_setから銘柄コードを取得 ---
# `tbl_codelist` から全銘柄コードを取得（スクリーニング対象銘柄リスト）
codes = db.read_code_all(cursor, "tbl_codelist")

# --- 4. スクリーンニング処理 ---
today = datetime.date.today()  # 今日の日付を取得
screening_results = []         # 買いシグナルの銘柄を格納するリスト

for code in codes:
    table_name = f"tbl_{code}"  # 銘柄ごとのテーブル名
    query = f"SELECT datetime, open, high, low, close, volume FROM {table_name} WHERE datetime >= '2022-01-01' ORDER BY datetime ASC"
    df = pd.read_sql_query(query, conn, parse_dates=["datetime"])
    df.set_index("datetime", inplace=True)
    print(code)
    # --- 5. RSI (4日) をワイルダー式で計算 ---
    def calculate_rsi_wilder(prices, window=4):
        """
        ワイルダー式の RSI を計算する関数（短期: 4日）
        """
        delta = prices.diff()
        gain = delta.clip(lower=0)  # 上昇分
        loss = -delta.clip(upper=0) # 下落分
        avg_gain = gain.rolling(window=window, min_periods=window).mean()
        avg_loss = loss.rolling(window=window, min_periods=window).mean()
        
        rsi = pd.Series(np.nan, index=prices.index)
        
        # RSI の初期値を設定
        for i in range(window, len(prices)):
            if i == window:
                current_avg_gain = avg_gain.iloc[i]
                current_avg_loss = avg_loss.iloc[i]
            else:
                current_avg_gain = (current_avg_gain * (window - 1) + gain.iloc[i]) / window
                current_avg_loss = (current_avg_loss * (window - 1) + loss.iloc[i]) / window
            
            # 平均損失が 0 の場合、RSI は 100
            if current_avg_loss == 0:
                rsi.iloc[i] = 100
            else:
                rs = current_avg_gain / current_avg_loss
                rsi.iloc[i] = 100 - (100 / (1 + rs))
        
        return rsi

    df['RSI'] = calculate_rsi_wilder(df['close'])

    # --- 6. 移動平均・出来高移動平均の計算 ---
    df['MA25'] = df['close'].rolling(window=25, min_periods=25).mean()  # 25日移動平均
    df['vol_ma5'] = df['volume'].rolling(window=5, min_periods=5).mean()  # 出来高5日移動平均

    # --- 7. 局所最小値（All Local Minima）の検出 ---
    price = df["close"]
    prominence_val = np.std(price) * PEAK_PROMINENCE_FACTOR  # 価格の標準偏差を基準に prominence を設定
    distance_val = PEAK_DISTANCE  # 最低 10 日間の間隔を空ける
    min_indices, _ = find_peaks(-price.values, prominence=prominence_val, distance=distance_val)

    # --- 8. 「深いカップ」の条件を適用 ---
    deep_cup_minima = []  # 有効なカップの谷を格納
    for min_idx in min_indices:
        if min_idx < LOOKBACK_WINDOW:
            continue  # 過去のデータが不足している場合はスキップ

        # 過去 20 日間の最高値を取得
        start_idx = min_idx - LOOKBACK_WINDOW
        window_prices = price.iloc[start_idx:min_idx+1]
        max_price = window_prices.max()

        # 最高値からの下落率が DROP_THRESHOLD 以上であれば「深いカップ」と判断
        if (max_price - price.iloc[min_idx]) / max_price >= DROP_THRESHOLD:
            deep_cup_minima.append(min_idx)

    # --- 9. 買いシグナル検出 ---
    buy_signals = []
    for idx, current_price in enumerate(price):
        current_date = price.index[idx]

        # ① 出来高フィルタ（現在の出来高が過去5日平均の1.5倍未満なら除外）
        if idx >= 5 and df['volume'].iloc[idx] < 1.5 * df['vol_ma5'].iloc[idx]:
            continue
        
        # ② RSI フィルタ（短期 RSI が 10 以下）
        if df['RSI'].iloc[idx] > 10:
            continue

        # ③ カップの縁（有効な Rim Date）の確認
        valid_rim_dates = [price.index[candidate_idx] for candidate_idx in deep_cup_minima if price.index[candidate_idx] < current_date]

        if not valid_rim_dates:
            continue

        # 直近の有効なリムを取得
        rim_date = max(valid_rim_dates)
        rim_idx = price.index.get_loc(rim_date)
        rim_price = price.iloc[rim_idx]

        # ④ 現在価格がリム価格の許容範囲内なら買いシグナル
        if (rim_price * (1 - TOLERANCE)) <= current_price <= (rim_price * (1 + TOLERANCE)):
            buy_signals.append((current_date, current_price, rim_date, rim_price))

    # --- 10. 直近5日以内の買いシグナルをスクリーニング ---
    for current_date, current_price, rim_date, rim_price in buy_signals:
        if (today - current_date.date()).days <= 5:
            screening_results.append((code, current_date, current_price, rim_date, rim_price))
            print(f"銘柄コード: {code}, 買いシグナル日付: {current_date}, 現在価格: {current_price}, リム価格: {rim_price}, リム価格出現日付: {rim_date}")

# --- 11. スクリーンング結果を表示 ---
if screening_results:
    print("本日付近（5日以内）で買いシグナルが出ている銘柄：")
    for code, current_date, current_price, rim_date, rim_price in screening_results:
        print(f"銘柄コード: {code}, 買いシグナル日付: {current_date}, 現在価格: {current_price}, リム価格: {rim_price}, リム価格出現日付: {rim_date}")
    line_notify(screening_results)
else:
    print("本日付近（5日以内）で買いシグナルが出ている銘柄はありません。")

# --- 12. DB切断 ---
conn.close()
