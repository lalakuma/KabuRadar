####################################################################
# ① データベースのtbl_nameから銘柄コードを読みだす
# ② au Kabukomu のApiを使用して読み出した銘柄コードの株価情報を取得する
# ③ 取得した株価情報をデータベースに保存する（銘柄毎にテーブルを作成）
####################################################################
import pandas as pd
import KabukomApi.kabusapi_token as token
import KabukomApi.kabusapi_board as board
import KabukomApi.kabusapi_unregisterall as unregiall
import sqlight as db
import getConfig as conf
import logging

#----------------------------------------
# LOG設定
#----------------------------------------
sth = logging.StreamHandler()
flh = logging.FileHandler('../../output/log/debug.log')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
                    handlers=[sth, flh])
logger = logging.getLogger(__name__)
logger.info("処理 main_entry_kabukom_price を開始します。")

#--------------------------------------
# DBから全銘柄コードを取得
#--------------------------------------
# DBに接続
conn, cursor = db.connect_db()
# 全銘柄コードリスト取得
codes = db.read_code_all(cursor, "tbl_codelist")

#--------------------------------------
# KabukomApiで価格情報を取得
#--------------------------------------
# パスワード取得
apipasswd = conf.get_config(conf.CONF_SEC_KABUSAPI, conf.CONF_KEY_API_PASSWD)
# APIにてトークン取得
tkn = token.getToken(apipasswd)

skip = 0 # 0:スキップなし、1:スキップあり

for code in codes:
    #途中までスキップする場合に使用する
    if skip == 1:
        if code == '9042':
            skip = 0
        else:
            continue

    # 登録銘柄全削除（レジスト数エラー対策）
    unregiall.unregisterall(tkn["Token"])
    # APIにて現時点の板情報を取得する
    content = board.get_board(tkn["Token"], code)

    # エラーコードを検出した場合はパスして次のループに進む
    if 'Code' in content:
        continue

     # ['日付', 'コード', '始値', '高値', '安値', '終値', '終値調整', '出来高']を抽出
    lst_price = []
    date = content["CurrentPriceTime"]
    if date != None:
        df = pd.DataFrame(
            data=[{'datetime': date[0:10],
                'open': str(content["OpeningPrice"]),
                'high': str(content["HighPrice"]),
                'low': str(content["LowPrice"]),
                'close': str(content["CurrentPrice"]),
                'volume': str(content["TradingVolume"]),
                }])

        df_daily = df.set_index("datetime")

        # 個別株価情報テーブルを作成
        db.create_nametbl(conn, cursor, code)
        # 最新レコードのみを登録
        db.one_marge_df_records(conn, cursor, code, df_daily)
        print(code)
        print(df_daily)

        # API実行回数エラーにならないようにスリープを入れる
#        time.sleep(100/1000)    

logger.info("処理 main_entry_kabukom_price を終了します。")


