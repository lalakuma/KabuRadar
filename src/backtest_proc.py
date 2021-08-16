import pandas as pd
import mplfinance as mpf
import technical_MACD as tc_macd
import technical_RSI as tc_rsi
import sqlight as db
import numpy
import os
from datetime import datetime, date, timedelta

class KabInf:
    lst_result = []
    outdf = pd.DataFrame()
    win = 0                 # 勝ち数
    lose = 0                # 負け数
    income = 0              # 利益
    winrate = 0             # 勝率
    adopt_rsi = 0           # 採用RSI
    plusgain = 0            # 売却時の株価1000だとした場合のプラス利益金額(全コードPF計算用)
    minusgain = 0           # 売却時の株価1000だとした場合の損失金額(全コードPF計算用)
    pf = 0                  # プロフィットファクター

    #****************************
    # 初期処理
    #****************************
    def __init__(self, lineave=200, macd_offset=0, rsi_border=30, rsi_per=25, rsi_max=59, rsi_period=10, breakout=5, sell_period=3, past_chart=(-1200)):
        self.lineave = lineave              # 買いシグナルに使用する長期移動平均線(上昇時に買)
        self.macd_offset = macd_offset      # MACDとシグナルの開き
        self.rsi_border = rsi_border        # RSIの下限値。scr_rsi_perが無効（-1）の時に採用する。
        self.rsi_per = rsi_per              # RSIの下限を全体の%で決める時の値。-1の時はrsi_borderを使用。
        self.rsi_max = rsi_max              # 買シグナルを出す上限RSI
        self.rsi_period = rsi_period        # RSIの値を何日まで遡ってみるか
        self.breakout = breakout            # ブレイクアウト判定期間に使用する値
        self.sell_period = sell_period      # 買いポジション最大保持期間
        self.past_chart = past_chart        # 過去何日前までのチャートを使用するか
    #****************************
    # 勝率を取得する
    #****************************
    def get_winrate(self):
        # 勝率を算出
        if self.win == 0 and self.lose ==0:
            self.winrate = 0
        else:
            self.winrate = int((self.win / (self.win + self.lose)) * 100)

        return self.winrate 

    #***************************************
    # 解析に使用したパラメータをCSVに保存する
    #***************************************
    def write_prm_tocsv(self):

        tup_prm = { 'lineave' : (self.lineave),
                    'macd_offset' : (self.macd_offset),
                    'rsi_border' : (self.rsi_border),
                    'rsi_per' : (self.rsi_per),
                    'rsi_max' : (self.rsi_max),
                    'rsi_period' : (self.rsi_period),
                    'breakout' : (self.breakout),
                    'sell_period' : (self.sell_period),
                    'past_chart' : (self.past_chart)}
        print(tup_prm)
        strdt = datetime.strftime(datetime.now(), '%Y-%m-%d_%H%M%S')
        df_prm = pd.DataFrame(tup_prm,index=[datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S')])
        print(df_prm)
        print("../analys/設定_" + strdt + ".csv")

        analys_path = "../analys"#フォルダ名
        if not os.path.exists(analys_path):#ディレクトリがなかったら
            os.mkdir(analys_path)#作成したいフォルダ名を作成

        df_prm.to_csv("../analys/設定_" + strdt + ".csv", encoding="shift_jis")    

 
#***************************************
# 危険な上髭検出処理
# True:検出した、False:検出なし
#***************************************
def judge_danger_upper(close, open, high):
    ret = False
    # 上髭が長いときは危険なので購入しないようにする。
    # 但し実態の長さが株価の2%以上の時に判定として使う。(2%は要調整)
    line_solid = abs(close - open)              # 始値と現在値の差分から実線の長さを設定
    if line_solid >= (open * 0.02):
        if  close >= open:                      # 陽線の時
            # 陽線の実態よりも2倍以上の長い上髭がある時は購入しない
            line_upper = high - close           # 高値と現在値の差分を上髭に設定
            if line_upper > (line_solid * 2):
                ret = True    
        else:                                       # 陰線の時
            # 陰線の実態よりも上髭が長いときは購入しない
            line_upper = high - open            # 高値と始値の差分を上髭の設定
            if line_upper > line_solid:
                ret = True
    return ret   
#--------------------------------------
# DBから全銘柄コードを取得
#--------------------------------------
# DBに接続
conn, cursor = db.connect_db()

lst_low_rsi = []
lst_codes = []
judge_buy_moving = False

def backtst_proc(code, Prm):
    ret = 0
    buy_pos = 0
    buy_price = 0
    sell_pos = 0
    income = 0
    win = 0
    lose = 0
    pre_low = 0
    signal_sell = False     # 売りシグナル初期化
    cnt_holddays = 0
    plusgain = 0.0
    minusgain = 0.0
    buy_under = 0

    # 個別銘柄 期間データ取得
    today = date.today()                                                          # 今日(日付型)
    str_date_sta = datetime.strftime(today + timedelta(days = Prm.past_chart), '%Y-%m-%d')  # 1200日前
    str_date_end = datetime.strftime(today + timedelta(days = 1), '%Y-%m-%d')     # 明日
    str_today = datetime.strftime(today, '%Y-%m-%d')                              # 今日

    # 指定期間のデータをDBから読み出す
    df = db.read_rec_period(conn, cursor, str(code), str_date_sta, str_date_end)
    #df.columns = ["datetime","open","high","low","close","volume"]
    try:
        df['datetime'] = df['datetime'].astype('datetime64')
        df['open'] = df['open'].astype('int64')
        df['high'] = df['high'].astype('int64')
        df['low'] = df['low'].astype('int64')
        df['close'] = df['close'].astype('int64')
        df['volume'] = df['volume'].astype('int64')
        df['SMA5'] = df['close'].rolling(window=5).mean()               # 5日移動平均を追加
        df['SMA25'] = df['close'].rolling(window=25).mean()             # 25日移動平均を追加
        df['SMASET'] = df['close'].rolling(window=Prm.lineave).mean()   # 設定した移動平均を追加
    except:
        print(code + ": Error")
        return (-1)

    # 最新価格が10000を超える株は対象外とする（資金的にまだ早い）
    price = df["close"].values[-1]
    if price > 10000:
        return (-1)

    #日付をインデックスにして、必要なアイテム順に並び替え
    df_price = df.set_index("datetime").loc[:,["open","high","low","close","volume","SMA5","SMA25","SMASET"]]

    df_price["mark"] = ""
    df_price["buy"] = 0
    df_price["sell"] = 0
    df_price["sellgain"] = 0
    df_price["income"] = 0

    print("sell_period :", Prm.sell_period)

    # MACDとRSIを追加
    df_price = tc_macd.macd(df_price)
#    df_price = tc_rsi.rsi(df_price)
    df_price = tc_rsi.rsi_tradingview(df_price)

    if Prm.rsi_per != -1:
        Prm.adopt_rsi = tc_rsi.search_proper_rsi(df_price, Prm.rsi_per)
    else:
        Prm.adopt_rsi = Prm.rsi_border

    bkdf = pd.DataFrame()
    for row in df_price.itertuples():
        # 移動平均が算出可能な日付付近までスキップ
        wkdf= pd.DataFrame([row])
        bkdf = bkdf.append(wkdf,ignore_index=True)
        if numpy.isnan(wkdf["SMASET"].values) == True:
            continue

        # 最新のMACDとシグナルの値を取得
        macd = bkdf["MACD"].values[-1]
        sig = bkdf["Signal"].values[-1]

        # 終値取得
        i_open = row.open
        i_close = row.close
        i_low = row.low
        i_high = row.high
        i_sma5 = row.SMA5
        # 日付取得
        idx_date = row[0]

#        if(datetime.strftime(idx_date, '%Y-%m-%d') == '2020-08-04'):
#            print(bkdf)
        #----------------------
        # 売却処理
        #----------------------
        sellgain = 0                                # 1回の売却利益初期化
        if buy_pos > 0:
            # 保持日数をインクリメント
            cnt_holddays += 1
            bkdf["mark"].iloc[-1] = "継続"

            # 購入時のローソク足が陽線の場合、購入時の始値を下回ったら売り
            # 購入時のローソク足が陰線の場合、購入時の安値を下回ったら売り
#            if buy_under > i_open:
#                signal_sell = True
#                sell_value = i_open                 # この時は始値を売値にする

            danger = judge_danger_upper(i_close, i_open, i_high)
            # 買い保持期間を過ぎたら翌日の始まり値で売り
            if cnt_holddays >= Prm.sell_period:
                signal_sell = True
                sell_value = i_close
            # 始値が購入日の安値を下回ったら損切り
            elif (i_open < pre_low):
                signal_sell = True
                sell_value = i_open                 # この時は始値を売値にする            
            # 場中に購入日に設定した下限を下回ったら場中でも即損切り
            # 下限は購入日のローソク足が陽線なら始値、陰線なら安値としている
            elif buy_under > i_low:
                signal_sell = True
                sell_value = buy_under              # 購入時の安値を売値にする。購入時に逆指値で注文しておく。
            elif danger == True:
                signal_sell = True
                sell_value = i_close
            # MACD < SIGで売りシグナル(MACDのデッドクロス)
            elif (macd <= sig):
                signal_sell = True
                sell_value = i_close
            # 終値が前日の安値を下回ったら売り
            elif pre_low > i_close:
                signal_sell = True
                sell_value = i_close
            # 5日移動平均より下回ったら売り
            elif i_sma5 > i_close:
                signal_sell = True
                sell_value = i_close

            # 前日の安値を更新
            pre_low = row.low

            #-----------------------------
            # 売りシグナル検出時の処理
            #-----------------------------
            if signal_sell == True:
                # 利益を更新
                diff = sell_value - buy_price
                sellgain = (diff * 100)         # 売却利益を格納
                income = income + sellgain      # 収益に加算
                signal_sell = False
                # 買いポジ初期化
                buy_pos = 0
                buy_price = 0
                cnt_holddays = 0
                print(code, ":", str(idx_date.date())," RSI=", str(int(rsi)), "返売", str(diff))

                # 勝敗
                if sellgain > 0:
                    win += 1
                    # 後で全体のPFを求める為にプラスの利益を集計。(小数点以下1位まで)
                    # 全コード平滑化するために株価が1000だったらという体で計算しておく。
                    wkgain = (diff/(i_close)) * 1000
                    plusgain += wkgain
                else:
                    if sellgain < 0:
                        lose += 1    
                        # 後で全体のPFを求める為にマイナスの利益を集計。(小数点以下1位まで)
                        # 全コード平滑化するために株価が1000だったらという体で計算しておく。
                        wkgain = (diff/(i_close)) * 1000
                        minusgain += wkgain

                bkdf["mark"].iloc[-1] = "返売"

        #----------------------
        # 売買数と利益を出力
        #----------------------
        bkdf["buy"].iloc[-1] = buy_pos
        bkdf["sellgain"].iloc[-1] = sellgain
        bkdf["income"].iloc[-1] = income

        #----------------------
        # 移動平均判定
        #----------------------
        if judge_buy_moving == True:
            buy_smaset = 0 
            taildf = bkdf.tail(5)
            sma1 = taildf["SMASET"].values[0]
            sma2 = taildf["SMASET"].values[-1]
            if sma1 <= sma2:
                buy_smaset = 1 

            if buy_smaset == 0:
                continue
        #----------------------
        # RSI判定
        #----------------------
        # RSI上限判定
        nowrsi = row.RSI
        if nowrsi > Prm.rsi_max:
            continue

        # 14日前からのRSIを取得
        dfrsi = bkdf.tail(Prm.rsi_period)

        # 過去指定日間でRSIが指定値を下回っていたらRSIフラグを1にする
        buy_rsi = 0
        for i, row in dfrsi.iterrows():
            rsi = row["RSI"]
            if rsi <= Prm.adopt_rsi:
                buy_rsi = 1
                break

        if buy_rsi == 0:
            continue

        #----------------------
        # MACD判定
        #----------------------
        # MACD > SIGで買いシグナル
        buy_macd = 0
        if macd > sig + Prm.macd_offset:
            buy_macd = 1

        if buy_macd == 0:
            continue

        #----------------------
        # ブレイクアウト判定
        #----------------------
        buy_break = 0
        # 最後から指定期間分のレコードを取得
        breakdf = bkdf.tail(Prm.breakout)
        # 指定期間中の前日までで一番の高値を取得
        size = len(breakdf)
        breakdf = breakdf.head(size - 1)
        df_max = breakdf["high"].rolling(window=size-1).max()
        max = df_max.values[-1]

        # 現在の価格が前日までの指定期間の高値を超えている場合に買いシグナルON
        if i_close > max:
            buy_break = 1

        if buy_break == 0:
            continue

        #----------------------
        # この時は買わない判定
        #----------------------
        # 上髭が長いときは危険なので購入しないようにする。
        # 但し実態の長さが株価の2%以上の時に判定として使う。(2%は要調整)
        line_solid = abs(i_close - i_open)          # 始値と現在値の差分から実線の長さを設定
        if line_solid >= (i_open * 0.02):
            if  i_close >= i_open:                      # 陽線の時
                # 陽線の実態よりも2倍以上の長い上髭がある時は購入しない
                line_upper = i_high - i_close           # 高値と現在値の差分を上髭に設定
                if line_upper > (line_solid * 2):
                    continue    
            else:                                       # 陰線の時
                # 陰線の実態よりも上髭が長いときは購入しない
                line_upper = i_high - i_open            # 高値と始値の差分を上髭の設定
                if line_upper > line_solid:
                    continue 


        #----------------------
        # 買い付け処理
        #----------------------
        buy_pos += 1
        bkdf["buy"].iloc[-1] = buy_pos
        if buy_price == 0:
            pre_low = i_low
            buy_price = i_close
            bkdf["mark"].iloc[-1] = "新買"

        #--------------------------------------
        # ここまで残ったコードをリストに追加
        #--------------------------------------
        print(code, ":", str(idx_date.date())," RSI=", int(rsi), "新買")
        str_close = "¥{:,d}".format(i_close)
        lst_codes.append(str(code) + ":" + str(idx_date.date()) + " " + str_close)

        # 購入時のローソク足が陽線か陰線かを調べる。ローソク足の実態の下限値を取得する
        if i_close >= i_open:
            buy_under = i_open                      # 始値を下限とする
        else:
            buy_under = i_low                       # 安値を下限とする
#            buy_under = i_close                     # 終値を下限とする

    # 出力情報を格納
    Prm.lst_result = lst_codes
    Prm.outdf = bkdf
    Prm.win = win
    Prm.lose = lose
    Prm.income = income
    Prm.plusgain = int(round(plusgain, 1) * 100)     # 売却時の株価1000だとした場合のプラス利益金額を計算
    Prm.minusgain = int(round(minusgain, 1) * 100)   # 売却時の株価1000だとした場合の損失金額を計算
    if win != 0 or lose !=0:
        Prm.winrate = (win / (win + lose)) * 100
    else:
        Prm.winrate = 0

    # コード毎はサンプル数が少ないのであまり意味がないがPFを算出してみる。
    # 分母か分子が0の場合はエラーになってしまうので-1とする。
    if plusgain != 0 and minusgain != 0:
        wkpf = plusgain / abs(minusgain)
    else:
        if plusgain == 0:
            wkpf = 0
        else:
            wkpf = plusgain
        
    Prm.pf = '{:.1f}'.format(wkpf)

    return ret

# テスト用
#lst_result, outdf, win, lose, income = backtst_proc(9984, 3)

