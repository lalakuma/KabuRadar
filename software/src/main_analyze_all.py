import common_def as DEF
import sqlight as db
import backtest_proc as bktst
import main_write_shuukei_csv as shuukei
import getPeriodKabu as pkabu
import pandas as pd
import getConfig as conf
import os
import glob
import logging
import sys
############################################
# 結果をCSVファイルに書き込む
############################################
def write_csv(dt, kekka_path):
    if dt.entrycnt != 0:
        winrate = bktst.KabInf.get_winrate(dt)
        wlstr = "_rsi"+ str(dt.adopt_rsi) + \
                "_W" + str(dt.win) + "L" + str(dt.lose) + \
                "_" + str(winrate) + "%_YEN" + str(dt.income) + \
                "_PF" + str(dt.pf) + \
                "_pg" + str(dt.plusgain) + \
                "_mg" + str(dt.minusgain)
                    
        dt.outdf.to_csv(kekka_path + "/code" + str(code) + wlstr + ".csv", encoding="shift_jis")    

pd.set_option('display.max_columns', 20)

#----------------------------------------
# 起動引数取得
#----------------------------------------
# バッチファイルから渡された引数を格納したリストの取得
argvs = sys.argv
if len(argvs) > 1:
    stance = argvs[1]
else:
    stance = 'NONE'
#----------------------------------------
# LOG設定
#----------------------------------------
sth = logging.StreamHandler()
flh = logging.FileHandler('../../output/log/debug.log')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
                    handlers=[sth, flh])
logger = logging.getLogger(__name__)

if stance == 'HI':
    str_stance = '高勝率モードで'
elif stance == 'LO':
    str_stance = '低勝率高回転モードで'
else:
    str_stance = '引数なしで'

logger.info("処理 main_analyze_all を" + str_stance + "開始します。")

#----------------------------------------
# DBより解析対象銘柄を全て取得
#----------------------------------------
# DBに接続
conn, cursor = db.connect_db()
# 全銘柄コードリスト取得
codes = db.read_code_all(cursor, "tbl_codelist")

#----------------------------------------
# 設定ファイルより解析期間を取得
#----------------------------------------
scrsec = conf.CONF_SEC_SCR
PAST_PERIOD = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_PAST_PERIOD)) * (-1)

#----------------------------------------
# メイン処理
#----------------------------------------
for offset in range(1):
    # 各パラメータをセットする
    cls_dt = bktst.KabInf(sell_period = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_SELL_PERIOD)),
                            breakout = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_BREAK_PERIOD)),
                            break_offset = float(conf.get_config(scrsec, conf.CONF_KEY_SCR_BREAK_OFSET)), 
                            macd_offset = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_MACD_OFSET)), 
                            lineave = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_LINEAVE)), 
                            past_period = PAST_PERIOD, 
                            rsi_period = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_RSI_PERIOD)),
                            rsi_border = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_RSI_BORDER)), 
                            rsi_max = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_RSI_MAX)), 
                            rsi_per = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_RSI_PER)))

    #--------------------------
    # 結果格納フォルダパス取得
    #--------------------------
    exec_mode = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_EXEC_MODE))   # 実行モード(0:テスト用、1:本番用)
    # 結果保存用のパスを取得
    if exec_mode == 1:  # 本番モードの時
        kekka_path = conf.get_config(conf.CONF_SEC_SHUUKEI, conf.CONF_KEY_PATH_HONBAN)
    else:               # テストモードの時
        kekka_path = conf.get_config(conf.CONF_SEC_SHUUKEI, conf.CONF_KEY_PATH_SHUUKEI)
        kekka_path = kekka_path + str(offset) + "\\" #フォルダ名    

    if os.path.exists(kekka_path):     # ディレクトリがない場合
        # 全てのCSVファイルを削除
        for filename in  glob.glob(kekka_path + '*.csv'):
            os.remove(filename)
        # 集計ファイルを削除
        if (stance == 'NONE') and (os.path.exists(kekka_path + '集計_NONE.xlsx')):
            os.remove(kekka_path + '集計_NONE.xlsx')
        if (stance == 'HI') and (os.path.exists(kekka_path + '集計_HI.xlsx')):
            os.remove(kekka_path + '集計_HI.xlsx')
        if (stance == 'LO') and (os.path.exists(kekka_path + '集計_LO.xlsx')):
            os.remove(kekka_path + '集計_LO.xlsx')

    cls_dt.write_prm_tocsv(kekka_path)      # パラメータをCSVに保存
    one_shot = 0    # 単発処理モード 0:無効、0以外:単発処理する銘柄コードを設定する

    CD_NIKKEI = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_IND_CODE))
    ind_code = CD_NIKKEI
    ENA_IND = conf.get_config(scrsec, conf.CONF_KEY_JDG_IND)
    df_indicator = pd.DataFrame()
    # 指標が有効な場合
    if ENA_IND == '1':
        # 指標株価を取得する
        df_indicator = pkabu.getPeriodKabuData(ind_code, PAST_PERIOD, conn, cursor)

    # 設定テーブル 全データ取得
    df_set = db.read_rec_all(conn, cursor, "tbl_code_set")
    df_set = df_set.set_index('code')

    # =====================================================
    # メインループ処理
    # =====================================================
    # 銘柄コードリストに登録されている全コードに対して処理を行う
    for code in codes:
        print("CODE=", code)

        #codeが無効に設定されている場合は処理しない
        code_ena = df_set.at[str(code), 'Enable']
        if code_ena == 0:
            continue

        # 売りシグナル = 0：保持期間なし(5日移動平均以下まで)、1～4：数値が指定保持期間、5：保持期間も移動平均もなしでMACDクロスで判定

        # 単発処理が有効な場合はコードを設定する
        if one_shot != 0:
            code = one_shot

        result = bktst.backtst_proc(code,
                df_indicator,
                cls_dt, 
                req_sb_mode = int(conf.get_config(scrsec, conf.CONF_KEY_SCR_SELLBUY)),  # 売買モード
                jdg_candle = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_CAND)),      # ローソク足判定
                jdg_ind = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_IND)),          # 指標銘柄判定
                jdg_mov = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_MOV)),          # 移動平均線判定
                jdg_rsi = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_RSI)),          # RSI判定
                jdg_macd = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_MACD)),        # MACD判定
                jdg_brk = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_BRK)),          # ブレイク判定
                jdg_berd = int(conf.get_config(scrsec, conf.CONF_KEY_JDG_BERD)))        # 髭判定
        if result == -1:
            continue

        # CSVに出力
        write_csv(cls_dt, kekka_path)

        # 単発処理が有効な場合は1回でループを抜ける
        if one_shot != 0:
            break

    # 集計処理
    shuukei.shuukei_toCsv(kekka_path)
    lst_shuukei = shuukei.shuukei_makeExl(kekka_path, stance)

# DBクローズ
db.close_db(conn)
