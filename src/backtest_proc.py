import common_def as DEF
import pandas as pd
import mplfinance as mpf
import technical_MovingAve as tc_movave
import technical_Bollinger as tc_bb
import technical_BreakOut as tc_break
import technical_Beard as tc_beard
import technical_MACD as tc_macd
import technical_RSI as tc_rsi
import sqlight as db
import numpy
import os
from datetime import datetime, date, timedelta

#****************************
# クラス定義
#****************************
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
    entrycnt = 0            # 購入カウント

    #****************************
    # 初期処理
    #****************************
    def __init__(self, lineave=200, macd_offset=0, rsi_border=30, rsi_per=25, rsi_max=59, rsi_period=10, breakout=5, sell_period=3, past_period=(-1200)):
        self.lineave = lineave              # 買いシグナルに使用する長期移動平均線(上昇時に買)
        self.macd_offset = macd_offset      # MACDとシグナルの開き
        self.rsi_border = rsi_border        # RSIの下限値。scr_rsi_perが無効（-1）の時に採用する。
        self.rsi_per = rsi_per              # RSIの下限を全体の%で決める時の値。-1の時はrsi_borderを使用。
        self.rsi_max = rsi_max              # 買シグナルを出す上限RSI
        self.rsi_period = rsi_period        # RSIの値を何日まで遡ってみるか
        self.breakout = breakout            # ブレイクアウト判定期間に使用する値
        self.sell_period = sell_period      # 買いポジション最大保持期間
        self.past_period = past_period        # 過去何日前までのチャートを使用するか
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
                    'past_period' : (self.past_period)}
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

def backtst_proc(code, df_indicator, Prm, req_sb_mode = DEF.MODE_BOTH, jdg_candle = False, jdg_ind = False, jdg_bolin = False, jdg_mov=False, jdg_rsi=False, jdg_macd=False, jdg_brk=False, jdg_berd=False):
    ret = 0
    buy_pos = 0
    buy_price = 0
    sell_price = 0
    sell_pos = 0
    income = 0
    win = 0
    lose = 0
    pre_low = 0
    pre_high = 0
    kessai_buy = False     # 買いポジション決済フラグ
    kessai_sell = False    # 売りポジション決済フラグ
    cnt_buyholddays = 0
    plusgain = 0.0
    minusgain = 0.0
    loss_line = 0
    ind_presma5 = 0
    ind_presma75 = 0
    ind_preclose = 0
    i_presma25 = 0
    entrycnt = 0

    sb_mode = DEF.MODE_BUY  # 初期値は買い
    
    if req_sb_mode != DEF.MODE_BOTH:
    	sb_mode = req_sb_mode
    
    # 個別銘柄 期間データ取得
    today = date.today()                                                          # 今日(日付型)
    str_date_sta = datetime.strftime(today + timedelta(days = Prm.past_period), '%Y-%m-%d')  # 1200日前
    str_date_end = datetime.strftime(today + timedelta(days = 1), '%Y-%m-%d')     # 明日
    str_today = datetime.strftime(today, '%Y-%m-%d')                              # 今日

#    str_date_sta = '2016-01-01'
#    str_date_end = '2016-12-31'
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

    if len(df) == 0:
        return (-1)
    price = df["close"].values[-1]
    # 最新価格が10000を超える株は対象外とする（資金的にまだ早い）
    if price > 10000:
        return (-1)

    #日付をインデックスにして、必要なアイテム順に並び替え
    df_price = df.set_index("datetime").loc[:,["open","high","low","close","volume","SMA5","SMA25","SMASET"]]
    df_price["mark"] = ""
    df_price["buy"] = 0
    df_price["buygain"] = 0
    df_price["sell"] = 0
    df_price["sellgain"] = 0
    df_price["income"] = 0
    
    # 指標銘柄も日付をインデックスにする
    #df_indicator= df_indicator.set_index("datetime").loc[:,["close","SMA5","SMA25","SMA75"]]

    print("sell_period :", Prm.sell_period)

    # MACDとRSIを追加
    df_price = tc_macd.macd(df_price)
#    df_price = tc_rsi.rsi(df_price)				# SBI證券アプリで見るRSIに近い計算方法
    df_price = tc_rsi.rsi_tradingview(df_price)		# Tradingviewで見るRSIに近い計算方法
    df_price = tc_bb.Bollinger(df_price)

#    print(df_price)

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

        #----------------------
        # 日付取得
        #----------------------
        idx_date = row[0]
    
        #----------------------
        # 最新のMACDとシグナルの値を取得
        #----------------------
        macd = bkdf["MACD"].values[-1]
        sig = bkdf["Signal"].values[-1]
            
        #----------------------
        # 各時点の値を取得
        #----------------------
        i_open = row.open                           # 終値取得
        i_close = row.close                         # 終値取得
        i_low = row.low                             # 安値取得
        i_high = row.high                           # 高値取得
        i_sma5 = row.SMA5                           # 5日移動平均値取得
        i_sma25 = row.SMA25                         # 25日移動平均値取得


        #----------------------
        # 指標銘柄判定
        #----------------------
        if jdg_ind == True:
            try:
                ind_sma5 = int(df_indicator.at[str(idx_date.date()), "SMA5"][0])
                ind_sma75 = int(df_indicator.at[str(idx_date.date()), "SMA75"][0])
                ind_close = df_indicator.at[str(idx_date.date()), "close"][0]
            except:
                print(str(idx_date.date()),'指標移動平均値取得エラー')
                ind_sma5 = ind_presma5
                ind_sma75 = ind_presma75
                ind_close = ind_preclose

            # 要求売買モードが両建てモードではない場合
            if req_sb_mode != DEF.MODE_BOTH:
	            # 買いモードの時
	            if sb_mode == DEF.MODE_BUY:
	                # 指標が75日線より低い場合は購入しない
	                if ind_sma75 > ind_close:
	                    continue
	            # 売りモードの時
	            if sb_mode == DEF.MODE_SELL:
	                # 指標が75日線より高い場合は購入しない
	                if ind_sma75 < ind_close:
	                    continue
            # 要求売買モードが両建てモードの場合、売買モードを設定
            else:
            	# 指標銘柄のMACDで売買モードを決める　（今一だった）
#                ind_macd = df_indicator["MACD"].values[-1]
#                ind_sig = df_indicator["Signal"].values[-1]
#                if ind_macd > ind_sig:
#                    sb_mode = DEF.MODE_BUY
#                else:
#                    sb_mode = DEF.MODE_SELL
            	# 該当銘柄のMACDで売買モードを決める macd > sigで買いだとパフォーマンスが悪かったので逆にした（でも今一だった）
#                if macd > sig:
#                    sb_mode = DEF.MODE_SELL
#                else:
#                    sb_mode = DEF.MODE_BUY
                #if ind_sma5 > ind_close:       (75のほうがちょっとよかった)
                # 指標が75日線より低い場合は売りモード
                if ind_sma75 > ind_close:
                # 指標の移動平均値が前日よりも低ければ売りモード
#                if  ind_presma5 > ind_sma5:    (75のほうがちょっとよかったけど5の上下よりはいい)
#                if i_sma25 < i_presma25:
                    sb_mode = DEF.MODE_SELL
                else:
                    sb_mode = DEF.MODE_BUY

            # 前回値を更新
            ind_presma5 = ind_sma5
            ind_presma75 = ind_sma75
            ind_preclose = ind_close
            i_presma25 = i_sma25
        else: # 指標判定が有効でない時は自銘柄の短期とで売買を判定する
            # 両建ての場合
            if req_sb_mode == DEF.MODE_BOTH:
                # 5日移動平均線より低ければ売りモード
                if  i_sma5 > i_close:
                    sb_mode = DEF.MODE_SELL
                else:
                    sb_mode = DEF.MODE_BUY

    
        if(datetime.strftime(idx_date, '%Y-%m-%d') == '2021-09-03'):
            print(bkdf)
        #==============================================================================================
        # 売却処理
        #==============================================================================================

        #-----------------------
        # 売りポジションがある時	(※現状は翌日始値売りにのみ対応)
        #-----------------------
        sellgain = 0                            # 1回の売却利益初期化
        if sell_pos > 0:
            # 売り保持期間を0にした場合は購入日翌日の始値で売り （1(終値まで持つ)にしたらパフォーマンス落がちた）
            if 0 == Prm.sell_period:
                kessai_sell = True
                sell_kessai_val = i_open

            #-----------------------------
            # 決済処理
            #-----------------------------
            if kessai_sell == True:
                # 利益を更新
                diff = sell_price - sell_kessai_val
                sellgain = (diff * 100)         # 売却利益を格納
                income = income + sellgain      # 収益に加算
                kessai_sell = False
                # 売りポジ初期化
                sell_pos = 0
                sell_price = 0
#                cnt_sellholddays = 0
                print(code, ":", str(idx_date.date()), "返買", str(diff))

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

                bkdf["mark"].iloc[-1] = "返買"

        #-----------------------
        # 買いポジションがある時
        #-----------------------
        buygain = 0                                 # 1回の売却利益初期化
        if buy_pos > 0:
            # 保持日数をインクリメント
            cnt_buyholddays += 1
            bkdf["mark"].iloc[-1] = "継続"

            # 購入時のローソク足が陽線の場合、購入時の始値を下回ったら売り
            # 購入時のローソク足が陰線の場合、購入時の安値を下回ったら売り
#            if loss_line > i_open:
#                kessai_buy = True
#                buy_kessai_val = i_open                 # この時は始値を売値にする

            danger = judge_danger_upper(i_close, i_open, i_high)
            # 買い保持期間を0にした場合は購入日翌日の始値で売り
            if 0 == Prm.sell_period:
                kessai_buy = True
                buy_kessai_val = i_open
            # 買い保持期間を過ぎたら売り
            elif cnt_buyholddays >= Prm.sell_period:
                kessai_buy = True
                buy_kessai_val = i_close
            # 始値が購入日の安値を下回ったら損切り
            elif (i_open < pre_low):
                kessai_buy = True
                buy_kessai_val = i_open                 # この時は始値を売値にする            
            # 場中に購入日に設定した下限を下回ったら場中でも即損切り
            # 下限は購入日のローソク足が陽線なら始値、陰線なら安値としている
            elif loss_line > i_low:
                kessai_buy = True
                buy_kessai_val = loss_line              # 購入時の安値を売値にする。(購入時に逆指値で注文しておく必要あり)
            elif danger == True:
                kessai_buy = True
                buy_kessai_val = i_close
            # MACD < SIGで売りシグナル(MACDのデッドクロス)
            elif (macd <= sig):
                kessai_buy = True
                buy_kessai_val = i_close
            # 終値が前日の安値を下回ったら売り
            elif pre_low > i_close:
                kessai_buy = True
                buy_kessai_val = i_close
            # 5日移動平均より下回ったら売り
            elif i_sma5 > i_close:
                kessai_buy = True
                buy_kessai_val = i_close

            # 前日の安値を更新
            pre_low = row.low

            #-----------------------------
            # 決済処理
            #-----------------------------
            if kessai_buy == True:
                # 利益を更新
                diff = buy_kessai_val - buy_price
                buygain = (diff * 100)         # 売却利益を格納
                income = income + buygain      # 収益に加算
                kessai_buy = False
                # 買いポジ初期化
                buy_pos = 0
                buy_price = 0
                cnt_buyholddays = 0
                print(code, ":", str(idx_date.date()), "返売", str(diff))

                # 勝敗
                if buygain > 0:
                    win += 1
                    # 後で全体のPFを求める為にプラスの利益を集計。(小数点以下1位まで)
                    # 全コード平滑化するために株価が1000だったらという体で計算しておく。
                    wkgain = (diff/(i_close)) * 1000
                    plusgain += wkgain
                else:
                    if buygain < 0:
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
        bkdf["buygain"].iloc[-1] = buygain
        bkdf["sell"].iloc[-1] = sell_pos
        bkdf["sellgain"].iloc[-1] = sellgain
        bkdf["income"].iloc[-1] = income

        #===========================================================================#
        # ここから購入判定処理
        #===========================================================================#
        #----------------------
        # ローソク足判定
        #----------------------
        if jdg_candle == True:
            # ローソクが陽線か陰線かを判別
            diff = i_close - i_open             # 始値と現在値の差分から実線の長さを設定
            if diff >= 0:
                line_kind = 1                   # ライン種別を陽線に設定
            else:
                line_kind = 0                   # ライン種別を陰線に設定

            # ローソクの大きさが1%未満は処理しない (2%にしたら悪くなった)
            if abs(diff) < abs(i_close * 0.01):
                continue

            # 買いモードかつローソク足が陰線は処理しない
            if sb_mode == DEF.MODE_BUY and line_kind == 0:
                continue
            # 売りモードかつローソク足が陽線は処理しない
            if sb_mode == DEF.MODE_SELL and line_kind == 1:
                continue

        #----------------------
        # ボリンジャー判定
        #----------------------
        if jdg_bolin == True:
            #------------------------------------------------------------
            # 指定期間内でボリンジャーバンドで2σを大きく超えている日があること
            # ない(False)場合は終了
            #------------------------------------------------------------
            if tc_bb.jdg_Bollinger_over2(sb_mode, bkdf, 10) == False:
                continue
            #--------------------------------------------------------
            # 当日高値値がボリンジャーバンドで3σを大きく超えていないことを確認 
            # 超えている(True)場合は終了
            #--------------------------------------------------------
            if tc_bb.jdg_Bollinger_over3(sb_mode, bkdf, i_high) == True:
                continue
    
        #----------------------
        # 移動平均判定
        #----------------------
        if jdg_mov == True:
            if tc_movave.jdg_movave_trend(sb_mode, bkdf) == 0:
                continue
        #----------------------
        # RSI判定
        #----------------------
        if jdg_rsi == True:         
            # 指定期間前からのRSIを取得
            dfrsi = bkdf.tail(Prm.rsi_period)
            # RSIの現在値が購入許可できる水準かを判定
            if tc_rsi.jdg_rsi_level(sb_mode, dfrsi, Prm.adopt_rsi) == 0:
                continue
            # 過去指定期間でRSIが指定値を閾値を超えたらRSIシグナルスイッチを1にする
            if tc_rsi.jdg_rsi_entered(sb_mode, dfrsi, Prm.adopt_rsi) == 0:
                continue
        #----------------------
        # MACD判定
        #----------------------
        if jdg_macd == True:                  
            # MACDのクロスが発生した後かを判定
            if tc_macd.jdg_macd_cross(sb_mode, bkdf, Prm.macd_offset) == 0:
                continue
        #----------------------
        # ブレイクアウト判定
        #----------------------
        if jdg_brk == True:
            dfrsi = bkdf.rename(columns={'Index': 'datetime'})
            if tc_break.jdg_break_out(sb_mode, dfrsi, Prm.breakout, i_close) == 0:
                continue
        #----------------------
        # 髭判定
        #----------------------
        if jdg_berd == True:
            if tc_beard.jdg_beard(sb_mode, i_open, i_high, i_low, i_close) == 0:
                continue

        #========================
        # 新規購入処理
        #========================
        # 買いモードの時
        if sb_mode == DEF.MODE_BUY:
            buy_pos += 1
            entrycnt +=1
            bkdf["buy"].iloc[-1] = buy_pos
            if buy_price == 0:
                pre_low = i_low
                buy_price = i_close
                bkdf["mark"].iloc[-1] = "新買"
            #--------------------------------------
            # ここまで残ったコードをリストに追加
            #--------------------------------------
            print(code, ":", str(idx_date.date()), "新買")
            str_close = "¥{:,d}".format(i_close)
            lst_codes.append(str(code) + ":" + str(idx_date.date()) + " " + str_close)

            # 購入時のローソク足が陽線か陰線かを調べる。購入日のローソク足から損切ラインを設定する
            if i_close >= i_open:
                loss_line = i_open                      # 始値を下限とする
            else:
                loss_line = i_low                       # 安値を下限とする
        # 売りモードの時
        else:
            sell_pos += 1
            entrycnt +=1
            bkdf["sell"].iloc[-1] = sell_pos
            if sell_price == 0:
                pre_high = i_high
                sell_price = i_close
                bkdf["mark"].iloc[-1] = "新売"
            #--------------------------------------
            # ここまで残ったコードをリストに追加
            #--------------------------------------
            print(code, ":", str(idx_date.date()), "新売")
            str_close = "¥{:,d}".format(i_close)
            lst_codes.append(str(code) + ":" + str(idx_date.date()) + " " + str_close)

            # 購入時のローソク足が陽線か陰線かを調べる。購入日のローソク足から損切ラインを設定する
            if i_close >= i_open:                       # 陽線の時
                loss_line = i_high                      # 高値を損切ラインとする
            else:                                       # 陰線の時
                loss_line = i_close                     # 終値を下限とする

    #========================
    # CSVに出力する情報を格納
    #========================
    Prm.lst_result = lst_codes
    Prm.outdf = bkdf
    Prm.win = win
    Prm.lose = lose
    Prm.income = income
    Prm.entrycnt = entrycnt
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

    return ret, lst_codes

# テスト用
#lst_result, outdf, win, lose, income = backtst_proc(9984, 3)

