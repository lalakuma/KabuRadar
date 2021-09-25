import urllib.request
import json
import pprint

def kabusapi_sendorder_margin_new(token, reqdat):
    obj = { 'Password': '123456',       # 1.注文パスワード
            'Symbol': '9433',           # 2.銘柄コード
            'Exchange': 1,              # 3.市場コード (1:東証[固定])
            'SecurityType': 1,          # 4.商品種別 (1:株式[固定])
            'Side': 2,                  # 5.売買区分 (1:売, 2:買)
            'CashMargin': 2,            # 6.信用区分 (1:現物, 2:新規, 3:返済)
            'MarginTradeType': 1,       # 7.信用取引区分 (1:制度信用, 2:一般信用(長期), 3:一般信用(デイトレ))
            'DelivType': 0,             # 8.受渡区分 (0:指定なし[信用新規時], 1:自動振替, 2:お預り金[信用返済時])
            'AccountType': 4,           # 9.口座種別 (2:一般, 4:特定[固定], 12:法人)
            'Qty': 100,                 # 10.注文数量
            'FrontOrderType': 16,       # 11.執行条件 (16:引成(後場))
            'Price': 0,                 # 12.注文価格 (成行の時は0を指定)
            'ExpireDay': 0,             # 13.注文有効期限
            'ReverseLimitOrder': {      # 14.逆指値注文
                                'TriggerSec': 2, #1.発注銘柄 2.NK225指数 3.TOPIX指数
                                'TriggerPrice': 30000,
                                'UnderOver': 2, #1.以下 2.以上
                                'AfterHitOrderType': 2, #1.成行 2.指値 3. 不成
                                'AfterHitPrice': 8435
                                }
        }
    json_data = json.dumps(obj).encode('utf-8')

    url = 'http://localhost:18080/kabusapi/sendorder'
    req = urllib.request.Request(url, json_data, method='POST')
    req.add_header('Content-Type', 'application/json')
#    req.add_header('X-API-KEY', 'ed94b0d34f9441c3931621e55230e402')
    req.add_header('X-API-KEY', token)

    try:
        with urllib.request.urlopen(req) as res:
            print(res.status, res.reason)
            for header in res.getheaders():
                print(header)
            print()
            content = json.loads(res.read())
            pprint.pprint(content)
    except urllib.error.HTTPError as e:
        print(e)
        content = json.loads(e.read())
        pprint.pprint(content)
    except Exception as e:
        print(e)

    return content
