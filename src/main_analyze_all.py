import common_def as DEF
import sqlight as db
import backtest_proc as bktst
import main_write_shuukei_csv as shuukei
import getPeriodKabu as pkabu
from datetime import datetime, date, timedelta
############################################
# 結果をCSVファイルに書き込む
############################################
def write_csv(dt):
    if dt.win == 0 and dt.lose == 0:
        print(str(code) + " is none")
    else:
        winrate = bktst.KabInf.get_winrate(dt)
        wlstr = "_rsi"+ str(dt.adopt_rsi) + \
                "_W" + str(dt.win) + "L" + str(dt.lose) + \
                "_" + str(winrate) + "%_YEN" + str(dt.income) + \
                "_PF" + str(dt.pf) + \
                "_pg" + str(dt.plusgain) + \
                "_mg" + str(dt.minusgain)
                    
        dt.outdf.to_csv("../analys/code" + str(code) + wlstr + ".csv", encoding="shift_jis")    

# DBに接続
conn, cursor = db.connect_db()
# 全銘柄コードリスト取得
codes = db.read_code_all(cursor, "tbl_codelist")

#PAST_PERIOD=(-4600)     # 過去4600日間のデータを検証 (MAX4700[2021/08/26現在] 2009年1月5日開始)
PAST_PERIOD=(-1000)     # 過去1000日間のデータを検証 (MAX4700[2021/08/26現在] 2009年1月5日開始)
cls_dt = bktst.KabInf(sell_period = 0,
                        rsi_max=100, 
                        rsi_period = 14,
                        breakout=5, 
                        macd_offset=5, 
                        lineave=100, 
                        past_period=PAST_PERIOD, 
                        rsi_per=30)
cls_dt.write_prm_tocsv()      # パラメータをCSVに保存
testmode = 0    # 単発テストモード 1:有効、0:無効

CD_NIKKEI = 1321
code = CD_NIKKEI

# 指標株価を取得する
df_nikkei = pkabu.getPeriodKabuData(code, PAST_PERIOD, conn, cursor)

# 設定テーブル 全データ取得
df_set = db.read_rec_all(conn, cursor, "tbl_code_set")
df_set = df_set.set_index('Code')

# 銘柄コードリストに登録されている全コードに対して処理を行う
for code in codes:
    #codeが無効に設定されている場合は処理しない
    code_ena = df_set.at[str(code), 'Enable']
    if code_ena == 0:
        continue


    # 対象銘柄に対するインデックス銘柄を設定する（今は日経225ETF）
    df_indicator = df_nikkei

    # 売りシグナル = 0：保持期間なし(5日移動平均以下まで)、1～4：数値が指定保持期間、5：保持期間も移動平均もなしでMACDクロスで判定
    #-----------------------
    # バックテストの実行
    #-----------------------
    if testmode == 1:
        ### 単発テスト用 ↓↓↓↓ STA ################################################
        code = 4523
#        cls_dt = bktst.KabInf(sell_period = 1, rsi_max=100, breakout=5, macd_offset=5, lineave=200, past_period=(-3000), rsi_per=30)
        cls_dt = bktst.KabInf(sell_period = 0,
                                rsi_max=100, 
                                rsi_period = 14,
                                breakout=5, 
                                macd_offset=5, 
                                lineave=100, 
                                past_period=PAST_PERIOD, 
                                rsi_per=30)
        result = bktst.backtst_proc(code,
                                cls_dt, 
                                sb_mode = DEF.MODE_BUY, 
                                jdg_mov=False, 
                                jdg_rsi=False, 
                                jdg_macd=False, 
                                jdg_brk=True, 
                                jdg_berd=True)            # テスト実行処理
        if result == -1:
            continue
        else:
            # CSVに出力
            write_csv(cls_dt)
            break
        ### 単発テスト用 ↑↑↑↑ END ################################################
    else:
        result = bktst.backtst_proc(code,
                                df_indicator,
                                cls_dt, 
                                req_sb_mode = DEF.MODE_BOTH, 
                                jdg_ind=True,               # 指標銘柄判定
                                jdg_mov=False,              # 移動平均線判定
                                jdg_rsi=False,              # RSI判定
                                jdg_macd=False,             # MACD判定
                                jdg_brk=True,               # ブレイク判定
                                jdg_berd=True)              # 髭判定
        if result == -1:
            continue
   
    # CSVに出力
    write_csv(cls_dt)

# DBクローズ
db.close_db(conn)

# 集計処理
shuukei.shuukei_toCsv()
shuukei.shuukei_makeExl()