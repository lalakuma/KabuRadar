####################################################################
# auカブコム証券を利用して株の売買を行う。
# ① トークンを取得
####################################################################
import KabukomApi.kabusapi_token as token
import KabukomApi.kabusapi_sendorder_margin_pay_ClosePositionOrder as margin_pay
import getConfig as conf
import logging
import KabukomApi.kabusapi_positions as positions
 
##############################################
# カブコムAPIでポジション決済
##############################################
def kabukom_settle(logger):
    # パスワード取得
    apipasswd = conf.get_config(conf.CONF_SEC_KABUSAPI, conf.CONF_KEY_API_PASSWD)
    trdpasswd = conf.get_config(conf.CONF_SEC_KABUSAPI, conf.CONF_KEY_TRD_PASSWD)
    # APIにてトークン取得
    tkn = token.getToken(apipasswd)
    lst_positions = positions.kabukom_positions(tkn["Token"])

    for posi in lst_positions:
        code = posi['Symbol']
        posId = posi['ExecutionID']
        HoldQty = posi['HoldQty']
        LeavesQty = posi['LeavesQty']
        Qty = LeavesQty - HoldQty
        side = posi['Side']
        if side == '2':
            k_side = '1'
        else:
            k_side = '2'

        # -------------------
        # 決済パラメータ設定
        # -------------------
        reqData = { 
                'Password': trdpasswd,          # 1.注文パスワード
                'Symbol': code,                 # 2.銘柄コード
                'Exchange': 1,                  # 3.市場コード (1:東証[固定])
                'SecurityType': 1,              # 4.商品種別 (1:株式[固定])
                'Side': k_side,                 # 5.売買区分 (1:売, 2:買)
                'CashMargin': 3,                # 6.信用区分 (1:現物, 2:新規, 3:返済)
                'MarginTradeType': 1,           # 7.信用取引区分 (1:制度信用, 2:一般信用(長期), 3:一般信用(デイトレ))
                'DelivType': 2,                 # 8.受渡区分 (0:指定なし[信用新規時], 1:自動振替, 2:お預り金[信用返済時])
                'AccountType': 4,               # 9.口座種別 (2:一般, 4:特定[固定], 12:法人)
                'Qty': Qty,                     # 10.注文数量
#                'ClosePositionOrder': 0,       # 11.日付（古い順）、損益（高い順） 
                'ClosePos_Id': posId,           # 11-1.建玉ID
                'ClosePos_Qty': Qty,            # 11-2.建玉数量
                'FrontOrderType': 13,           # 12.執行条件 (13:寄成(前場), 16:引成(後場))
                'Price': 0,                     # 13.注文価格 (成行の時は0を指定)
                'ExpireDay': 0,                 # 14.注文有効期限
            }
        print(reqData)
        ret = margin_pay.kabusapi_sendorder_margin_payClose(tkn["Token"], reqData, logger) 

###########################
# メイン
###########################
#----------------------------------------
# LOG設定
#----------------------------------------
sth = logging.StreamHandler()
flh = logging.FileHandler('../../output/log/debug.log')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
                    handlers=[sth, flh])
logger = logging.getLogger(__name__)
logger.info("処理 main_kabustation_kessai を開始します。")

#----------------------------------------
# 決済処理
#----------------------------------------
kabukom_settle(logger)