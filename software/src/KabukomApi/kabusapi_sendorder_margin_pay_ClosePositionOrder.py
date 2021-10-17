import urllib.request
import json
import pprint

def kabusapi_sendorder_margin_payClose(token, reqdat, logger):
    obj = { 'Password': reqdat['Password'],
            'Symbol': reqdat['Symbol'],
            'Exchange': reqdat['Exchange'],
            'SecurityType': reqdat['SecurityType'],
            'Side': reqdat['Side'],
            'CashMargin': reqdat['CashMargin'],
            'MarginTradeType': reqdat['MarginTradeType'],
            'DelivType': reqdat['DelivType'],
            'AccountType': reqdat['AccountType'],
            'Qty': reqdat['Qty'],
#            'ClosePositionOrder': reqdat['ClosePositionOrder'],    # ClosePositionsとどちらか一方に指定
            "ClosePositions": [
            {
            "HoldID": reqdat['ClosePos_Id'],
            "Qty": reqdat['ClosePos_Qty']
            }
            ],            
            'FrontOrderType': reqdat['FrontOrderType'],
            'Price': reqdat['Price'],
            'ExpireDay': reqdat['ExpireDay'],
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
    
    logger.info("[決済] content=%s",content)    
    return content
