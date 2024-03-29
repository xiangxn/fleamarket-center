import requests
import json
from center.database.model import User as UserModel


class Gateway:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    def post(self, uri=None, data=None):
        url = self.config['url']
        if uri:
            if url.endswith("/"):
                url += uri
            else:
                url += "/" + uri
        header = {"token": self.config['token']}
        res = None
        try:
            res = requests.post(url, data=json.dumps(data), headers=header)
            if res.status_code == 200:
                res = res.json()
        except Exception as e:
            self.logger.Error("!!! An error occurred while requesting the gateway", e, screen=True)
        return res

    def createAccount(self, nickname, owner, active, authkey, referrer, phone_hash, en_phone):
        data = {
            "owner_pubkey": owner,
            "active_pubkey": active,
            "nickname": nickname,
            "en_phone": en_phone,
            "phone_hash": phone_hash,
            "referrer": referrer,
            "auth_key": authkey
        }
        res = self.post(uri="create_account", data=data)
        return res

    def createAddress(self, order_id, symbol):
        data = {"order_id": order_id, "symbol": symbol}
        res = self.post(uri="create_address", data=data)
        return res

    def broadcast(self, trx, sign=False):
        data = {"sign": sign, "trx": trx}
        res = self.post(uri="broadcast", data=data)
        return res

    def getUser(self, eosid=None, uid=None, limit=1):
        query = {"limit": limit}
        if eosid:
            query['eosid'] = eosid
        if uid:
            query['uid'] = uid
        res = self.post(uri="get_user", data=query)
        return res

    def getReferral(self, eosid):
        user = UserModel.objects(eosid=eosid).first()
        if not user:
            user = self.getUser(eosid=eosid)
            if user and len(ref['rows']) > 0:
                return (int(ref['rows'][0]['uid']), user['rows'][0]['eosid'])
            else:
                return (0, "")
        return (user.userid, user.eosid)
