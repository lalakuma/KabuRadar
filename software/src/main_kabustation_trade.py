####################################################################
# auカブコム証券を利用して株の売買を行う。
# ① トークンを取得
####################################################################
import KabukomApi.kabusapi_token as token
import KabukomApi.kabusapi_margin as margin
import KabukomApi.kabusapi_sendorder_margin_new as margin_new
import KabukomApi.kabusapi_sendorder_margin_pay_ClosePositionOrder as margin_pay
import getConfig as conf
import main_write_shuukei_csv as shuukei
import datetime
import time
import line
import logging
 
##############################################
# カブコムAPIで新規購入
##############################################
def kabukom_entry(lst_data, logger):
    # パスワード取得
    apipasswd = conf.get_config(conf.CONF_SEC_KABUSAPI, conf.CONF_KEY_API_PASSWD)
    trdpasswd = conf.get_config(conf.CONF_SEC_KABUSAPI, conf.CONF_KEY_TRD_PASSWD)
    # APIにてトークン取得
    tkn = token.getToken(apipasswd)

    for tdy in lst_data:
        # 新規買い対象のみ処理する。それ以外は処理しない。
        mark = tdy["mark"]
        if "新買" in mark:
            side = "2"
            chMgn = 2
            DlvType = 0
            qty = 100       # 注文数量。今は100固定だけどそのうち株価によって調整する。
        elif "新売" in mark:
            side = "1"
            chMgn = 2
            DlvType = 0
            qty = 100       # 注文数量。今は100固定だけどそのうち株価によって調整する。
        else:
            continue 

        code = tdy['code']                  # コード取得
        MTrdType = 1
        reqData = { 
            'Password': trdpasswd,          # 1.注文パスワード
            'Symbol': code,                 # 2.銘柄コード
            'Exchange': 1,                  # 3.市場コード (1:東証[固定])
            'SecurityType': 1,              # 4.商品種別 (1:株式[固定])
            'Side': side,                   # 5.売買区分 (1:売, 2:買)
            'CashMargin': chMgn,            # 6.信用区分 (1:現物, 2:新規, 3:返済)
            'MarginTradeType': MTrdType,    # 7.信用取引区分 (1:制度信用, 2:一般信用(長期), 3:一般信用(デイトレ))
            'DelivType': DlvType,           # 8.受渡区分 (0:指定なし[信用新規時], 1:自動振替, 2:お預り金[信用返済時])
            'AccountType': 4,               # 9.口座種別 (2:一般, 4:特定[固定], 12:法人)
            'Qty': qty,                     # 10.注文数量
            'FrontOrderType': 16,           # 11.執行条件 (13:寄成(前場), 16:引成(後場))
            'Price': 0,                     # 12.注文価格 (成行の時は0を指定)
            'ExpireDay': 0,                 # 13.注文有効期限
        }

        ret = margin_new.kabusapi_sendorder_margin_new(tkn["Token"], reqData, logger)
        time.sleep(1)

###########################
# メイン
###########################
kekka_path = conf.get_config(conf.CONF_SEC_SHUUKEI, conf.CONF_KEY_PATH_HONBAN)
df, lst_shuukei = shuukei.decide_trade(kekka_path)

lst_trade = []

#----------------------------------------
# LOG設定
#----------------------------------------
sth = logging.StreamHandler()
flh = logging.FileHandler('../../output/log/debug.log')
 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
                    handlers=[sth, flh])
logger = logging.getLogger(__name__)
logger.info("処理 main_kabustation_trade を開始します。")

#----------------------------------------
# 当日の取引データのみを抽出してリスト化
#----------------------------------------
for trd in lst_shuukei:
    # 今日の日付を取得
    strtoday = str(datetime.date.today())
#    strtoday = '2021-10-01'

    # 取引日付を取得
    trddate = trd["_1"]
    strdate =  trddate[0:10]
    if strtoday != strdate:
        continue
    lst_trade.append(trd)

# 平日限定で以下の処理を行う
iWeek = datetime.datetime.today().isoweekday()
if iWeek != 6 and iWeek != 7:            #土日以外 
    #----------------------------------------
    # LINEで結果を通知
    #----------------------------------------
    lst_linenoti = []
    for trd in lst_trade:
        if trd["mark"] == "新買" or trd["mark"] == "新売":
            lst_linenoti.append("[" + str(trd["code"]) + "]" + trd["mark"] + " PF:" + str(trd["PF"]) + " ¥{:,d}".format(trd["close"]))

#    line.line_notify(lst_linenoti)

    #----------------------------------------
    # 指定の時間帯であれば取引を実行する
    #----------------------------------------
    dt = datetime.datetime.now()
    tm = dt.time()

    # 14:30～15：00の間に実行された場合はエントリー処理を行う
    if tm < datetime.time(15,0,0) and tm > datetime.time(14,30,0):
        kabukom_entry(lst_trade, logger)
