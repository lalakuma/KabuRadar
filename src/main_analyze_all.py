import sqlight as db
import backtest_proc as bktst
import main_write_shuukei_csv as shuukei

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

ptype = "day"
cls_dt = bktst.KabInf(sell_period = 3,      # 1
                            rsi_max=100, 
                            rsi_period = 6,    #10→14→8→6
                            breakout=6, 
                            macd_offset=5, 
                            lineave=1, 
                            past_chart=(-400), 
                            rsi_per=10)
cls_dt.write_prm_tocsv()      # パラメータをCSVに保存
testmode = 0    # 単発テストモード 1:有効、0:無効

# 銘柄コードリストに登録されている全コードに対して処理を行う
for code in codes:

    # 売りシグナル = 0：保持期間なし(5日移動平均以下まで)、1～4：数値が指定保持期間、5：保持期間も移動平均もなしでMACDクロスで判定
    #-----------------------
    # バックテストの実行
    #-----------------------
    if testmode == 1:
        ### 単発テスト用 ↓↓↓↓ STA
        code = 2269
#        cls_dt = bktst.KabInf(sell_period = 1, rsi_max=100, breakout=5, macd_offset=5, lineave=200, past_chart=(-3000), rsi_per=30)
        cls_dt = bktst.KabInf(sell_period = 1, rsi_max=100, breakout=5, macd_offset=5, lineave=1, past_chart=(-400), rsi_per=30)
        result = bktst.backtst_proc(code, cls_dt)            # テスト実行処理
        if result == -1:
            continue
        else:
            # CSVに出力
            write_csv(cls_dt)
            break
        ### 単発テスト用 ↑↑↑↑ END
    else:
        result = bktst.backtst_proc(code, cls_dt)            # テスト実行処理
        if result == -1:
            continue
   
    # CSVに出力
    write_csv(cls_dt)

# DBクローズ
db.close_db(conn)

# 集計処理
shuukei.shuukei_toCsv()