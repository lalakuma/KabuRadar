import urllib.request
import json
import pprint


def get_board(token, code):
    		
#	url = 'http://localhost:18080/kabusapi/board/2124@1'
	url = 'http://localhost:18080/kabusapi/board/' + code + '@1'
	req = urllib.request.Request(url, method='GET')
	req.add_header('Content-Type', 'application/json')
#	req.add_header('X-API-KEY', 'ecc3973cd5ec42ecac25500bf26ecefc')
	req.add_header('X-API-KEY', token)

	try:
	    with urllib.request.urlopen(req) as res:
#	        print(res.status, res.reason)
#	        for header in res.getheaders():
#	            print(header)
#	        print()
	        content = json.loads(res.read())
#	        pprint.pprint(content)
	except urllib.error.HTTPError as e:
	    print(e)
	    content = json.loads(e.read())
	    pprint.pprint(content)
	except Exception as e:
	    print(e)

	return content
