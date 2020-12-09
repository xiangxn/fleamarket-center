import sys
sys.path.append('../center')
import time
import hashlib
import requests
import urllib
import json
from eospy.utils import decimalToBinary


class TestSMS(object):
    def test_sms(self):
        phone = "18580555547"
        code = "123456"
        project = "06kla4"
        api_url = "https://api.mysubmail.com/message/xsend.json"
        app_id = "58648"
        app_key = "bc630f47b7d4e602c27915532aae3918"
        sms_vars = json.dumps({"code": code, "time": "120秒"})
        data = {'appid': app_id, 'project': project, 'sign_type': "sha1", 'timestamp': str(int(time.time())), 'to': phone}  #'sign_version': "2",
        query = urllib.parse.urlencode(data)
        query = "{}{}{}&vars={}{}{}".format(app_id, app_key, query, sms_vars, app_id, app_key)
        print(query)
        signature = hashlib.sha1(query.encode('utf-8')).hexdigest()
        data['vars'] = sms_vars
        data["signature"] = signature
        print(data)
        res = requests.post(api_url, json=data, headers={'Content-Type': "application/json"})
        print(res.json())
