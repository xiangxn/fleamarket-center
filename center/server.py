from concurrent import futures
import grpc
import time
from center.logger import Logger
import pymongo
import re
import random
import asyncio
import time

from bitsflea_pb2_grpc import add_BitsFleaServicer_to_server, BitsFleaServicer
from bitsflea_pb2 import RegisterRequest, RegisterReply, User, BaseReply

from center.gateway import Gateway
from center.utils import Utils
from center.graphene.keys import PrivateKey, PublicKey
from center.graphene.memo import encode_memo, decode_memo


class Server(BitsFleaServicer):
    
    def __init__(self, config):
        self.logger = Logger()
        self.config = config
        self._connectDB(self.config['mongo'])
        self.gateway = Gateway(self.config['gateway'], self.logger)

    def _connectDB(self, config):
        _client = pymongo.MongoClient(config['host'], config['port'])
        _db = _client[config['db']]
        self.db_users = _db['users']
        self.db_sms = _db['sms']
        
    def SendSmsCode(self, request, context):
        is_phone = re.match(r"^1[3456789]\d{9}$", request.phone)
        if is_phone:
            code = int("".join(random.sample('0123456789',6)))
            self.db_sms.update({"phone":request.phone}, {"phone":request.phone,"code":code,"time":int(time.time())}, upsert=True)
            # TODO: 处理发送模板类型与发送短信
            return BaseReply(code=0,msg="success")
        return BaseReply(code=1,msg="Phone numbers not currently supported")
    
    def _encrypt_phone(self, phone, active):
        nonce = "".join(random.sample('0123456789',8))
        priKey = PrivateKey(self.config['encrypt_key'])
        pubKey = PublicKey(active)
        en_msg = encode_memo(priKey, pubKey, nonce, phone)
        return nonce+en_msg
    
    def _decrypt_phone(self, phone_encrypt, active):
        nonce = phone_encrypt[0:8]
        en_msg = phone_encrypt[8:]
        priKey = PrivateKey(self.config['encrypt_key'])
        pubKey = PublicKey(active)
        return decode_memo(priKey, pubKey, nonce, en_msg)
    
    def _register(self, phone, en_phone, owner, active, referral):
        user = None
        name = None
        referral_name = ""
        #创建eos id
        result = self.gateway.createAccount(owner, active)
        if result:
            #获取引荐人
            ref = self.gateway.getUser(eosid=referral)
            #print("ref: ", ref)
            if ref and len(ref['rows']) > 0:
                referral = int(ref['rows'][0]['uid'])
                referral_name = ref['rows'][0]['eosid']
            else:
                referral = int(self.config['referrer'][0])
                referral_name = self.config['referrer'][1]
            #处理手机号
            phone_hash = Utils.sha256(bytes(phone, "utf8"))
            #print("phone_hash: ", phone_hash)
            if not en_phone:
                en_phone = self._encrypt_phone(phone, active)
                #print("en_phone: ", en_phone)
            name = result['name']
            #注册到平台
            payload = {
                "account": "bitsfleamain",
                "name": "reguser",
                "authorization": [{
                    "actor": "bitsfleamain",
                    "permission": "active",
                }],
                "data": {
                    "eosid": name,
                    "nickname": name,
                    "phone_hash": phone_hash,
                    "phone_encrypt": en_phone,
                    "referrer": referral
                }
            }
            trx = {"transaction":{"actions": [payload]}}
            #print("trx", trx)
            result = self.gateway.broadcast(trx, sign=True)
            #print("result", result)
            if result['status'] == "success":
                #获取注册信息
                res = self.gateway.getUser(eosid=name)
                if len(res['rows']) > 0:
                    user = res['rows'][0]
            else:
                return result
        return user, referral_name
        
        
    def Register(self, request, context):
        flag = False
        if self.config['use_sms']:
            sms_info = self.db_sms.find_one({"phone":request.phone})
            if sms_info and sms_info['code'] == request.smscode and (int(time.time())-sms_info['time'] <= 300):
                flag = True
        else:
            flag = True
        if flag and len(request.phone) > 0 and len(request.ownerpubkey) == 53 and len(request.actpubkey) == 53:
            m = RegisterReply()
            en_phone = None
            if hasattr(request, "phoneEncrypt"):
                en_phone = request.phoneEncrypt
            user_info, referral = self._register(request.phone, en_phone, request.ownerpubkey, request.actpubkey, request.referral)
            if user_info and "status" in user_info:
                if user_info['status'] != "failed":
                    m.msg = "registration successful"
                    m.data.userid = user_info['uid']
                    m.data.eosid = user_info['eosid']
                    m.data.phone = request.phone    #user_info['phone_encrypt']
                    m.data.status = user_info['status']
                    m.data.nickname = user_info['nickname']
                    m.data.creditValue = user_info['credit_value']
                    m.data.referrer = referral      #str(user_info['referrer'])
                    m.data.lastActiveTime = user_info['last_active_time']
                    m.data.postsTotal = user_info['posts_total']
                    m.data.sellTotal = user_info['sell_total']
                    m.data.buyTotal = user_info['buy_total']
                    m.data.referralTotal = user_info['referral_total']
                    m.data.point = user_info['point']
                    m.data.isReviewer = user_info['is_reviewer']
                else:
                    m.code = 101
                    m.msg = user_info['message']
            else:
                m.code = 500
                m.msg = "An error occurred while requesting the gateway"
            return m
        else:
            return BaseReply(code=2,msg="Invalid verification code") 


def bits_flea_run(config):
    # 这里通过thread pool来并发处理server的任务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # 将对应的任务处理函数添加到rpc server中
    add_BitsFleaServicer_to_server(Server(config), server)

    # 这里使用的非安全接口，世界gRPC支持TLS/SSL安全连接，以及各种鉴权机制
    server.add_insecure_port("[::]:{}".format(config['server_port']))
    server.start()
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        server.stop(0)