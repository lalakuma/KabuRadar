from math import fabs
import common_def as DEF
import pandas as pd
#import mplfinance as mpf
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
import getConfig as conf

#****************************
# クラス定義
#****************************
class KabInf:
    lst_result = []
    outdf = pd.DataFrame()
    winrate = 0             # 勝率
    adopt_rsi = 0           # 採用RSI
    pf = 0                  # プロフィットファクター
    entrycnt = 0            # 購入カウント

    #****************************
    # 初期処理
    #****************************
    def __init__(self, lineave=200, break_offset=0, macd_offset=0, rsi_border=30, rsi_per=25, rsi_max=59, rsi_period=10, breakout=5, sell_period=3, past_period=(-1200)):
        self.lineave = lineave                  # 買いシグナルに使用する長期移動平均線(上昇時に買)
        self.macd_offset = macd_offset          # MACDとシグナルの開き
        self.break_offset = break_offset        # ブレイクアウトオフセット。上限を何%超えたか。(1/100で計算)
        self.rsi_border = rsi_border            # RSIの下限値。scr_rsi_perが無効（-1）の時に採用する。
        self.rsi_per = rsi_per                  # RSIの下限を全体の%で決める時の値。-1の時はrsi_borderを使用。
        self.rsi_max = rsi_max                  # 買シグナルを出す上限RSI
        self.rsi_period = rsi_period            # RSIの値を何日まで遡ってみるか
        self.breakout = breakout                # ブレイクアウト判定期間に使用する値
        self.sell_period = sell_period          # 買いポジション最大保持期間
        self.past_period = past_period          # 過去何日前までのチャートを使用するか
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
    def write_prm_tocsv(self, analys_path):

        tup_prm = { 'lineave' : (self.lineave),
                    'macd_offset' : (self.macd_offset),
                    'rsi_border' : (self.rsi_border),
                    'rsi_per' : (self.rsi_per),
                    'rsi_max' : (self.rsi_max),
                    'rsi_period' : (self.rsi_period),
                    'breakout' : (self.breakout),
                    'sell_period' : (self.sell_period),
                    'past_period' : (self.past_period)}
        strdt = datetime.strftime(datetime.now(), '%Y-%m-%d_%H%M%S')
        df_prm = pd.DataFrame(tup_prm,index=[datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S')])

        if not os.path.exists(analys_path):     # ディレクトリがない場合
            os.mkdir(analys_path)               # フォルダを作成

        df_prm.to_csv(analys_path + "設定_" + strdt + ".csv", encoding="shift_jis")    

        
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
lastidx_bk = 0

# 株価情報クラス
class CodePrice:
    code = 0                            # 銘柄コード
    i_open = 0                          # 終値
    i_close = 0                         # 終値
    i_low = 0                           # 安値
    i_high = 0                          # 高値
    i_sma5 = 0                          # 5日移動平均値
    i_sma25 = 0                         # 25日移動平均値
    i_presma25 = 0                      # 25日移動平均値(前日)
    i_macd = 0                          # MACD
    i_sig = 0                           # シグナル

# トレード情報クラス
class TradeInfo:
    sb_mode = 0                         # 売買モード
    buy_price = 0                       # 買い価格
    buy_pos = 0                         # 買いポジション数
    sell_price = 0                      # 売り価格
    sell_pos = 0                        # 売りポジション数
    kessai_buy = False                  # 買いポジション決済フラグ
    kessai_sell = False                 # 売りポジション決済フラグ
    isreserved = 0                      # 予約有無(無：0、買：1、売：2)
    entrycnt = 0                        # エントリー回数
    win = 0                             # 勝ち数
    lose = 0                            # 負け数
    plusgain = 0                        # 売却時の株価1000だとした場合のプラス利益金額(全コードPF計算用)
    minusgain = 0                       # 売却時の株価1000だとした場合の損失金額(全コードPF計算用)
    income = 0                          # 利益

# 判定クラス
class Judge:
    jdg_candle = False
    jdg_ind = False
    jdg_bolin = False
    jdg_mov=False
    jdg_mov_pfct=False
    jdg_mov_push=False
    jdg_rsi=False
    jdg_macd=False
    jdg_brk=False
    jdg_berd=False

    def __init__(self, scrsec):
        
        self.jdg_candle = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_CAND))      # ローソク足判定
        self.jdg_ind = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_IND))          # 指標銘柄判定
        self.jdg_mov = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_MOV))          # 移動平均線判定
        self.jdg_mov_pfct = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_MOV_PFCT))# 移動平均線パーフェクトオーダー判定
        self.jdg_mov_push = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_MOV_PUSH))# 移動平均線押し目判定
        self.jdg_bolin = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_BOLIN))      # ボリンジャー判定
        self.jdg_rsi = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_RSI))          # RSI判定
        self.jdg_macd = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_MACD))        # MACD判定
        self.jdg_brk = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_BRK))          # ブレイク判定
        self.jdg_berd = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_BERD))        # 髭判定

#################################################################
# バックテストメイン処理
# 引数：code           銘柄コード
#     ：df_indicator   指標株価情報
#     ：Prm            パラメータ情報
# 戻り値：処理結果
#################################################################
def backtst_proc(code, df_indicator, Prm):
    scrsec = conf.CONF_SEC_SCR
    cp = CodePrice()
    ti = TradeInfo()
    jg = Judge(scrsec)
    
    cp.code = code
    ret = 0
#    pre_low = 0
    cnt_buyholddays = 0
    cp.plusgain = 0.0
    cp.minusgain = 0.0
    ind_presma5 = 0
    ind_presma75 = 0
    ind_preclose = 0
    i_presma25 = 0
    ti.isreserved = False         # 予約(True：エントリー予約あり、False：なし)

    req_sb_mode = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_SELLBUY))       # 売買モード
    ent_timing = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_ENT_TIMING))     # エントリータイミング

    if req_sb_mode != DEF.MODE_BOTH:
        ti.sb_mode = req_sb_mode
    
    # 個別銘柄 期間データ取得
    today = date.today()                                                          # 今日(日付型)
    str_date_sta = datetime.strftime(today + timedelta(days = Prm.past_period), '%Y-%m-%d')  # 1200日前
    str_date_end = datetime.strftime(today + timedelta(days = 1), '%Y-%m-%d')     # 明日
    str_today = datetime.strftime(today, '%Y-%m-%d')                              # 今日

#    str_date_sta = '2016-01-01'
#    str_date_end = '2016-12-31'
    # 指定期間のデータをDBから読み出す
    df = db.read_rec_period(conn, cursor, str(cp.code), str_date_sta, str_date_end)
    #df.columns = ["datetime","open","high","low","close","volume"]
    try:
        df['datetime'] = df['datetime'].astype('datetime64')
        df['open'] = df['open'].astype('int64')
        df['high'] = df['high'].astype('int64')
        df['low'] = df['low'].astype('int64')
        df['close'] = df['close'].astype('int64')
        df['volume'] = df['volume'].astype('int64')
        df['SMA5'] = df['close'].rolling(window=5).mean()               # 5日移動平均を追加
        if (jg.jdg_mov == True) or (jg.jdg_ind == True) :    
            df['SMA25'] = df['close'].rolling(window=25).mean()             # 25日移動平均を追加
            df['SMASET'] = df['close'].rolling(window=Prm.lineave).mean()   # 設定した移動平均を追加
    except:
        print(cp.code + ": Error")
        return (-1)

    if len(df) == 0:
        return (-1)
    price = df["close"].values[-1]
    # 最新価格が10000を超える株は対象外とする（資金的にまだ早い）
    if price > 10000:
        return (-1)

    #日付をインデックスにして、必要なアイテム順に並び替え
    if (jg.jdg_mov == True) or (jg.jdg_ind == True) :    
        df_price = df.set_index("datetime").loc[:,["open","high","low","close","volume","SMA5","SMA25","SMASET"]]
    else:
        df_price = df.set_index("datetime").loc[:,["open","high","low","close","volume","SMA5"]]
    df_price["mark"] = ""
    df_price["buy"] = 0
    df_price["buygain"] = 0
    df_price["sell"] = 0
    df_price["sellgain"] = 0
    df_price["income"] = 0
    
    # 指標銘柄も日付をインデックスにする
    #df_indicator= df_indicator.set_index("datetime").loc[:,["close","SMA5","SMA25","SMA75"]]

    # MACD追加
    if jg.jdg_macd == True:
        df_price = tc_macd.macd(df_price)
        
    # RSI追加
    if jg.jdg_rsi == True:
        df_price = tc_rsi.rsi_tradingview(df_price)		# Tradingviewで見るRSIに近い計算方法
    #    df_price = tc_rsi.rsi(df_price)				# SBI證券アプリで見るRSIに近い計算方法
        if Prm.rsi_per != -1:
            Prm.adopt_rsi = tc_rsi.search_proper_rsi(df_price, Prm.rsi_per)
        else:
            Prm.adopt_rsi = Prm.rsi_border

    # ボリンジャーバンド追加
    if jg.jdg_bolin == True:
        df_price = tc_bb.Bollinger(df_price)

    bkdf = pd.DataFrame()
    for row in df_price.itertuples():
    
        # 移動平均が算出可能な日付付近までスキップ
        wkdf= pd.DataFrame([row])
        bkdf = bkdf.append(wkdf,ignore_index=True)
        lastidx_bk = len(bkdf) - 1
        if (jg.jdg_mov == True) or (jg.jdg_ind == True) :    
            if numpy.isnan(wkdf["SMASET"].values) == True:
                continue
        else:
            if numpy.isnan(wkdf["SMA5"].values) == True:
                continue

        #----------------------
        # 日付取得
        #----------------------
        idx_date = row[0]
        if str(datetime.date(idx_date)) == '2022-01-18':
            a = 1
        #----------------------
        # 最新のMACDとシグナルの値を取得
        #----------------------
        if jg.jdg_macd == True:
            cp.i_macd = bkdf["MACD"].values[-1]
            cp.i_sig = bkdf["Signal"].values[-1]
            
        #----------------------
        # 前日値を保存
        #----------------------
        i_close_pre1 = cp.i_close

        #----------------------
        # 各時点の値を取得
        #----------------------
        cp.i_open = row.open                           # 始値取得
        cp.i_close = row.close                         # 終値取得
        cp.i_low = row.low                             # 安値取得
        cp.i_high = row.high                           # 高値取得
        cp.i_sma5 = row.SMA5                           # 5日移動平均値取得
        if jg.jdg_mov == True:
            cp.i_presma25 = cp.i_sma25
            cp.i_sma25 = row.SMA25                     # 25日移動平均値取得

        #----------------------
        # 指標銘柄判定
        #----------------------
        if jg.jdg_ind == True:
            try:
                dt = str(idx_date.date())

                ind_sma5 = int(df_indicator.loc[dt, "SMA5"])
                ind_sma75 = int(df_indicator.loc[dt, "SMA75"])
                ind_close = int(df_indicator.loc[dt, "close"])
            except:
                print(str(idx_date.date()),'指標移動平均値取得エラー')
                ind_sma5 = ind_presma5
                ind_sma75 = ind_presma75
                ind_close = ind_preclose

            # 要求売買モードが両建てモードではない場合
            if req_sb_mode != DEF.MODE_BOTH:
                # 買いモードの時
                if ti.sb_mode == DEF.MODE_BUY:
                    # 指標が75日線より低い場合は購入しない
                    if ind_sma75 > ind_close:
                        continue
	            # 売りモードの時
            if ti.sb_mode == DEF.MODE_SELL:
                    # 指標が75日線より高い場合は購入しない
                    if ind_sma75 < ind_close:
                        continue
            # 要求売買モードが両建てモードの場合、売買モードを設定
            else:
                # 指標銘柄のMACDで売買モードを決める　（今一だった）
#                ind_macd = df_indicator["MACD"].values[-1]
#                ind_sig = df_indicator["Signal"].values[-1]
#                if ind_macd > ind_sig:
#                    ti.sb_mode = DEF.MODE_BUY
#                else:
#                    ti.sb_mode = DEF.MODE_SELL
            	# 該当銘柄のMACDで売買モードを決める cp.i_macd > cp.i_sigで買いだとパフォーマンスが悪かったので逆にした（でも今一だった）
#                if cp.i_macd > cp.i_sig:
#                    ti.sb_mode = DEF.MODE_SELL
#                else:
#                    ti.sb_mode = DEF.MODE_BUY
                #if ind_sma5 > ind_close:       (75のほうがちょっとよかった)
                # 指標が75日線より低い場合は売りモード
                if ind_sma75 > ind_close:
                # 指標の移動平均値が前日よりも低ければ売りモード
#                if  ind_presma5 > ind_sma5:    (75のほうがちょっとよかったけど5の上下よりはいい)
                    ti.sb_mode = DEF.MODE_SELL
                else:
                    ti.sb_mode = DEF.MODE_BUY

            # 前回値を更新
            ind_presma5 = ind_sma5
            ind_presma75 = ind_sma75
            ind_preclose = ind_close
        elif jg.jdg_mov_pfct == True:   # パーフェクトオーダー判定ありの場合の売買モード切替
            # 両建ての場合
            if req_sb_mode == DEF.MODE_BOTH:
                # 25日移動平均線の傾きで決める
                if  cp.i_presma25 > cp.i_sma25: # 2
                    ti.sb_mode = DEF.MODE_SELL
                else:
                    ti.sb_mode = DEF.MODE_BUY
        else: # 指標判定が有効でない時は自銘柄の短期とで売買を判定する
            # 両建ての場合
            if req_sb_mode == DEF.MODE_BOTH:
                # 5日移動平均線より低ければ売りモード
                if  cp.i_sma5 > cp.i_close:
                    ti.sb_mode = DEF.MODE_SELL
                else:
                    ti.sb_mode = DEF.MODE_BUY

    
#        if(datetime.strftime(idx_date, '%Y-%m-%d') == '2021-10-28'):
#            print(bkdf)
        #==============================================================================================
        # 売却処理
        #==============================================================================================
        kessai_proc(cp, ti, jg, bkdf, Prm, row, idx_date, cnt_buyholddays)

        #**************************************************************************************************
        # 購入判定
        #**************************************************************************************************
        if ti.isreserved == False:
            # 売買シグナル判定処理
            jdg_rlt = judge_signal(cp, ti, jg, bkdf, Prm)
            if jdg_rlt == False:
                continue
        else:
            # 翌日購入指定の時、買シグナルON時の終値よりも翌日の始値が低く始まった場合は購入しない
            if ti.sb_mode == DEF.MODE_BUY:
                if i_close_pre1 >= cp.i_open:
                    # 予約解除
                    ti.isreserved = False
                    continue
            # 翌日購入指定の時、売シグナルON時の終値よりも翌日の始値が高く始まった場合は購入しない
            if ti.sb_mode == DEF.MODE_SELL:
                if i_close_pre1 <= cp.i_open:
                    # 予約解除
                    ti.isreserved = False
                    continue                
        #**************************************************************************************************
        # ここまで残ったものをエントリー対象とする。
        #**************************************************************************************************
        entry_proc(cp, ti, lst_codes, bkdf, lastidx_bk, idx_date, ent_timing)

    #========================
    # CSVに出力する情報を格納
    #========================
    Prm.lst_result = lst_codes
    Prm.outdf = bkdf
    Prm.win = ti.win
    Prm.lose = ti.lose
    Prm.income = ti.income
    Prm.entrycnt = ti.entrycnt
    Prm.plusgain = int(round(cp.plusgain, 1) * 100)     # 売却時の株価1000だとした場合のプラス利益金額を計算
    Prm.minusgain = int(round(cp.minusgain, 1) * 100)   # 売却時の株価1000だとした場合の損失金額を計算
    if ti.win != 0 or ti.lose !=0:
        Prm.winrate = (ti.win / (ti.win + ti.lose)) * 100
    else:
        Prm.winrate = 0

    # コード毎はサンプル数が少ないのであまり意味がないがPFを算出してみる。
    # 分母か分子が0の場合はエラーになってしまうので-1とする。
    if cp.plusgain != 0 and cp.minusgain != 0:
        wkpf = cp.plusgain / abs(cp.minusgain)
    else:
        if cp.plusgain == 0:
            wkpf = 0
        else:
            wkpf = cp.plusgain
        
    Prm.pf = '{:.1f}'.format(wkpf)

    return ret, lst_codes

# テスト用
#lst_result, outdf, ti.win, ti.lose, ti.income = backtst_proc(9984, 3)

#################################################################
# 売買シグナル判定処理
# 引数：cp  株価情報クラス
# 戻り値：なし
#################################################################
def kessai_proc(cp, ti, jg, bkdf, Prm, row, idx_date, cnt_buyholddays):
    #-----------------------
    # 売りポジションがある時	(※現状は翌日始値売りにのみ対応)
    #-----------------------
    sellgain = 0                            # 1回の売却利益初期化
    if ti.sell_pos > 0:
        # 売り保持期間を-1にした場合は購入日翌日の始値で売り
        if -1 == Prm.sell_period:
            ti.kessai_sell = True
            sell_kessai_val = cp.i_open
        # 買い保持期間を過ぎたら売り
        elif cnt_buyholddays >= Prm.sell_period:
            ti.kessai_sell = True
            sell_kessai_val = cp.i_close
        # MACD > SIGで売りシグナル(MACDのゴールデンクロス)
        elif (jg.jdg_macd == True) and (cp.i_macd >= cp.i_sig):
            ti.kessai_sell = True
            sell_kessai_val = cp.i_close
        # 5日移動平均より上回ったら売り
        elif cp.i_sma5 < cp.i_close:
            ti.kessai_sell = True
            sell_kessai_val = cp.i_close

        #-----------------------------
        # 決済処理
        #-----------------------------
        if ti.kessai_sell == True:
            # 利益を更新
            diff = ti.sell_price - sell_kessai_val
            sellgain = (diff * 100)         # 売却利益を格納
            ti.income = ti.income + sellgain      # 収益に加算
            ti.kessai_sell = False
            # 売りポジ初期化
            ti.sell_pos = 0
            ti.sell_price = 0
#                cnt_sellholddays = 0
            print(cp.code, ":", str(idx_date.date()), "返買", str(diff))

            # 勝敗
            if sellgain > 0:
                ti.win += 1
                # 後で全体のPFを求める為にプラスの利益を集計。(小数点以下1位まで)
                # 全コード平滑化するために株価が1000だったらという体で計算しておく。
                wkgain = (diff/(cp.i_close)) * 1000
                cp.plusgain += wkgain
            else:
                if sellgain < 0:
                    ti.lose += 1    
                    # 後で全体のPFを求める為にマイナスの利益を集計。(小数点以下1位まで)
                    # 全コード平滑化するために株価が1000だったらという体で計算しておく。
                    wkgain = (diff/(cp.i_close)) * 1000
                    cp.minusgain += wkgain

            bkdf.loc[lastidx_bk, "mark"] = "返買"

    #-----------------------
    # 買いポジションがある時
    #-----------------------
    buygain = 0                                 # 1回の売却利益初期化
    if ti.buy_pos > 0:
        # 保持日数をインクリメント
        cnt_buyholddays += 1
        bkdf.loc[lastidx_bk, "mark"] = "継続"

        # 危険な上髭判定
        danger = judge_danger_upper(cp.i_close, cp.i_open, cp.i_high)
        # 買い保持期間を-1にした場合は購入日翌日の始値で売り
        if -1 == Prm.sell_period:
            ti.kessai_buy = True
            buy_kessai_val = cp.i_open
        # 買い保持期間を過ぎたら売り
        elif cnt_buyholddays >= Prm.sell_period:
            ti.kessai_buy = True
            buy_kessai_val = cp.i_close
        # 始値が購入日の安値を下回ったら損切り
#            elif (cp.i_open < pre_low):
#                ti.kessai_buy = True
#                buy_kessai_val = cp.i_open                 # この時は始値を売値にする            
        elif danger == True:
            ti.kessai_buy = True
            buy_kessai_val = cp.i_close
        # MACD < SIGで売りシグナル(MACDのデッドクロス)
        elif (jg.jdg_macd == True) and (cp.i_macd <= cp.i_sig):
            ti.kessai_buy = True
            buy_kessai_val = cp.i_close
        # 終値が前日の安値を下回ったら売り
#            elif pre_low > cp.i_close:
#                ti.kessai_buy = True
#                buy_kessai_val = cp.i_close
        # 5日移動平均より下回ったら売り
        elif cp.i_sma5 > cp.i_close:
            ti.kessai_buy = True
            buy_kessai_val = cp.i_close

        # 前日の安値を更新
#        pre_low = row.low

        #-----------------------------
        # 決済処理
        #-----------------------------
        if ti.kessai_buy == True:
            # 利益を更新
            diff = buy_kessai_val - ti.buy_price
            buygain = (diff * 100)         # 売却利益を格納
            ti.income = ti.income + buygain      # 収益に加算
            ti.kessai_buy = False
            # 買いポジ初期化
            ti.buy_pos = 0
            ti.buy_price = 0
            cnt_buyholddays = 0
            print(cp.code, ":", str(idx_date.date()), "返売", str(diff))

            # 勝敗
            if buygain > 0:
                ti.win += 1
                # 後で全体のPFを求める為にプラスの利益を集計。(小数点以下1位まで)
                # 全コード平滑化するために株価が1000だったらという体で計算しておく。
                wkgain = (diff/(cp.i_close)) * 1000
                cp.plusgain += wkgain
            else:
                if buygain < 0:
                    ti.lose += 1    
                    # 後で全体のPFを求める為にマイナスの利益を集計。(小数点以下1位まで)
                    # 全コード平滑化するために株価が1000だったらという体で計算しておく。
                    wkgain = (diff/(cp.i_close)) * 1000
                    cp.minusgain += wkgain

            bkdf.loc[lastidx_bk, "mark"] = "返売"

    #----------------------
    # 売買数と利益を出力
    #----------------------
    bkdf.loc[lastidx_bk, "buy"] = ti.buy_pos
    bkdf.loc[lastidx_bk, "buygain"] = buygain
    bkdf.loc[lastidx_bk, "sell"] = ti.sell_pos
    bkdf.loc[lastidx_bk, "sellgain"] = sellgain
    bkdf.loc[lastidx_bk, "income"] = ti.income

#################################################################
# 売買シグナル判定処理
# 引数：cp  株価情報クラス
# 戻り値：なし
#################################################################
def judge_signal(cp, ti, jg, bkdf, Prm):
    #----------------------
    # ローソク足判定
    #----------------------
    if jg.jdg_candle == True:
        # ローソクが陽線か陰線かを判別
        diff = cp.i_close - cp.i_open             # 始値と現在値の差分から実線の長さを設定
        if diff >= 0:
            line_kind = 1                   # ライン種別を陽線に設定
        else:
            line_kind = 0                   # ライン種別を陰線に設定

        # ローソクの大きさが1%未満は処理しない (2%にしたら悪くなった)
        if abs(diff) < abs(cp.i_close * 0.01):
            return False

        # 買いモードかつローソク足が陰線は処理しない
        if ti.sb_mode == DEF.MODE_BUY and line_kind == 0:
            return False
        # 売りモードかつローソク足が陽線は処理しない
        if ti.sb_mode == DEF.MODE_SELL and line_kind == 1:
            return False

    #----------------------
    # ボリンジャー判定
    #----------------------
    if jg.jdg_bolin == True:
        #------------------------------------------------------------
        # 指定期間内で2回以上ボリンジャーバンドの2σ/-2σを超えているかを判定する
        # ない(False)場合は終了
        #------------------------------------------------------------
        if tc_bb.jdg_Bollinger_over(ti.sb_mode, bkdf, 3) == False:
            return False
        #------------------------------------------------------------
        # 指定期間内でボリンジャーバンドで2σを大きく超えている日があること
        # ない(False)場合は終了
        #------------------------------------------------------------
        if tc_bb.jdg_Bollinger_over2(ti.sb_mode, bkdf, 10) == False:
            return False
        #--------------------------------------------------------
        # 当日高値値がボリンジャーバンドで3σを大きく超えていないことを確認 
        # 超えている(True)場合は終了
        #--------------------------------------------------------
        if tc_bb.jdg_Bollinger_over3(ti.sb_mode, bkdf, cp.i_high) == True:
            return False

    #----------------------
    # 移動平均判定
    #----------------------
    if jg.jdg_mov == True:
        if tc_movave.jdg_movave_trend(ti.sb_mode, bkdf) == 0:
            return False
        #----------------------
        # パーフェクトオーダー判定
        #----------------------
        if jg.jdg_mov_pfct == True:
            if tc_movave.jdg_movave_PfctOder(ti.sb_mode, bkdf) == 0:
                return False
        #----------------------
        # 押し目判定
        #----------------------
        if jg.jdg_mov_push == True:
            if tc_movave.jdg_movave_Push(ti.sb_mode, bkdf, cp.i_close) == 0:
                return False

    #----------------------
    # RSI判定
    #----------------------
    if jg.jdg_rsi == True:         
        # 指定期間前からのRSIを取得
        dfrsi = bkdf.tail(Prm.rsi_period)
        # RSIの現在値が購入許可できる水準かを判定
        if tc_rsi.jdg_rsi_level(ti.sb_mode, dfrsi, Prm.adopt_rsi) == 0:
            return False
        # 過去指定期間でRSIが指定値を閾値を超えたらRSIシグナルスイッチを1にする
        if tc_rsi.jdg_rsi_entered(ti.sb_mode, dfrsi, Prm.adopt_rsi) == 0:
            return False
    #----------------------
    # MACD判定
    #----------------------
    if jg.jdg_macd == True:                  
        # MACDのクロスが発生した後かを判定
        if tc_macd.jdg_macd_cross(ti.sb_mode, bkdf, Prm.macd_offset) == 0:
            return False
    #----------------------
    # ブレイクアウト判定
    #----------------------
    if jg.jdg_brk == True:
        dfbreak = bkdf.rename(columns={'Index': 'datetime'})
        if tc_break.jdg_break_out2(ti.sb_mode, dfbreak, Prm.breakout, Prm.break_offset, cp.i_close) == 0:
#            if tc_break.jdg_break_out(ti.sb_mode, dfbreak, Prm.breakout, Prm.break_offset, cp.i_close) == 0:
            return False
    #----------------------
    # 髭判定
    #----------------------
    if jg.jdg_berd == True:
        if tc_beard.jdg_beard(ti.sb_mode, cp.i_open, cp.i_high, cp.i_low, cp.i_close) == 0:
            return False
            
    return True

#################################################################
# 新規購入処理
# 売買シグナルが発生した場合に購入処理を行う
# エントリータイミングが当日の場合は購入処理を行い、翌日の場合は予約のみ行う。
# 引数：cp  株価情報クラス
#     : ti  エントリー情報クラス
#     : lst_codes   購入情報リスト
#     : bkdf        コード情報データフレーム
#     : lastidx_bk  bkdfからlst_codesに登録した時の最終インデックス
#     : idx_date    日付
#     : ent_timing  エントリータイミング(0:当日、1:翌日)
# 戻り値：なし
#################################################################
def entry_proc(cp, ti, lst_codes, bkdf, lastidx_bk, idx_date, ent_timing):
    # 買いモードの時
    if ti.sb_mode == DEF.MODE_BUY:
        # エントリータイミングが翌日で予約なしの時
        if (ent_timing == 1) and (ti.isreserved == False):
            strtrd = "買シ"
            ti.isreserved = True                              # 予約ありに設定
        else:
            strtrd = "新買"
            ti.isreserved = False                             # 予約初期化
            ti.buy_pos += 1
            ti.entrycnt +=1
            bkdf.loc[lastidx_bk, "buy"] = ti.buy_pos
            if ti.buy_price == 0:
                # 当日購入指定の時は終値で購入
                if ent_timing == 0:
                    ti.buy_price = cp.i_close
                # 翌日購入指定の時は始値で購入
                elif ent_timing == 1:
                    ti.buy_price = cp.i_open

        bkdf.loc[lastidx_bk, "mark"] = strtrd
        add_entry_list(cp, lst_codes,idx_date, strtrd, ti.buy_price)

    # 売りモードの時
    else:

        # エントリータイミングが翌日で予約なしの時
        if (ent_timing == 1) and (ti.isreserved == False):
            strtrd = "売シ"
            ti.isreserved = True                              # 予約ありに設定
        else:
            ti.isreserved = False                             # 予約初期化
            ti.sell_pos += 1
            ti.entrycnt +=1
            bkdf.loc[lastidx_bk, "sell"] = ti.sell_pos
            strtrd = "新売"
            if ti.sell_price == 0:
                # 当日購入指定の時は終値で購入
                if ent_timing == 0:
                    ti.sell_price = cp.i_close
                # 翌日購入指定の時は始値で購入
                elif ent_timing == 1:
                    ti.sell_price = cp.i_open

        bkdf.loc[lastidx_bk, "mark"] = strtrd
        add_entry_list(cp, lst_codes,idx_date, strtrd, ti.sell_price)
    
#################################################################
# 新規購入時、購入情報リストに追加
# 引数:cp          株価情報クラス
#     : lst_codes   購入情報リスト
#     : idx_date    日付
#     : strtrd      トレード文字列
#     : trdval      トレード価格
# 戻り値：なし
#################################################################
def add_entry_list(cp, lst_codes,idx_date, strtrd, trdval):
    print(cp.code, ":", str(idx_date.date()), strtrd)
    str_fmt = "¥{:,d}".format(trdval)
    lst_codes.append(str(cp.code) + ":" + str(idx_date.date()) + " " + str_fmt)

