from concurrent import futures
import grpc
import time
from center.logger import Logger
import pymongo
import re
import random
import asyncio
import time
import json

from bitsflea_pb2_grpc import add_BitsFleaServicer_to_server, BitsFleaServicer
from bitsflea_pb2 import RegisterRequest, RegisterReply, User, BaseReply
from bitsflea_pb2 import SearchRequest, SearchReply
from bitsflea_pb2 import FollowRequest

from center.database.model import Follow as FollowModel
from center.database.model import User as UserModel

from center.gateway import Gateway
from center.utils import Utils

import mongoengine
from center.database.schema import schema

from center.database.model import Sms as SmsModel
from center.database.model import User as UserModel


class Server(BitsFleaServicer):
    
    def __init__(self, config):
        self.logger = Logger()
        self.config = config
        self._connectDB(self.config['mongo'])
        self.gateway = Gateway(self.config['gateway'], self.logger)

    def _connectDB(self, config):
        #连接mongoengine
        mongoengine.connect(db=config['db'], host=config['host'], port=config['port'])
        
    def SendSmsCode(self, request, context):
        is_phone = re.match(r"^1[3456789]\d{9}$", request.phone)
        if is_phone:
            code = "".join(random.sample('0123456789',6))
            sms = SmsModel.objects(phone=request.phone).first()
            if sms:
                sms.code = code
                sms.time = int(time.time())
                sms.save()
            else:
                SmsModel(phone=request.phone, code=code, time=int(time.time())).save()
            # TODO: 处理发送模板类型与发送短信
            return BaseReply(code=0,msg="success")
        return BaseReply(code=1,msg="Phone numbers not currently supported")
    
    def Search(self, request, context):
        if request.query:
            result = schema.execute(request.query)
            if result.data:
                sur = SearchReply()
                sur.data = json.dumps(result.data)
                return sur
            else:
                return SearchReply(code=1, msg="no data")
        else:
            return SearchReply(code=300, msg="Invalid query")
        
    def Transaction(self, request, context):
        if request.trx:
            sign = True if request.sign else False
            if sign:
                tmp_trx = json.loads(request.trx)['transaction']
                if len(tmp_trx['actions']) != 1 or tmp_trx['actions'][0]['account'] != self.config['sync_cfg']['contract'] or tmp_trx['actions'][0]['name'] != "publish":
                    return BaseReply(code=401,msg="This action has no permissions") 
            result = self.gateway.broadcast(request.trx, sign=sign)
            if result['status'] == "success":
                return BaseReply(code=0,msg="success")
            else:
                return BaseReply(code=500,msg=result['message'])
        return BaseReply(code=3,msg="Invalid paras") 
    
    def _register(self, phone, en_phone, owner, active, authkey, referral, nickname):
        user = None
        #获取引荐人
        (referral, referral_name) = self.gateway.getReferral(eosid=referral)
        #print("ref: ", ref)
        if not referral or not referral_name:
            referral = int(self.config['referrer'][0])
            referral_name = self.config['referrer'][1]
        #authkey
        if not authkey or len(authkey) != len(active):
            authkey = active
        #处理手机号
        phone_hash = Utils.sha256(bytes(phone, "utf8"))
        #print("phone_hash: ", phone_hash)
        if not en_phone:
            en_phone = Utils.encrypt_phone(phone, authkey, self.config['encrypt_key'])
        #创建eos id
        result = self.gateway.createAccount(nickname, owner, active, authkey, referral, phone_hash, en_phone)
        #print(result)
        if result:
            if result['status'] == "success":
                #获取注册信息
                res = self.gateway.getUser(eosid=result['name'])
                if len(res['rows']) > 0:
                    user = res['rows'][0]
                else:
                    user = result
                    user['message'] = "Has been successfully registered, waiting for data sync"
            else:
                user = result
        return user, referral_name
        
        
    def Register(self, request, context):
        flag = False
        if self.config['use_sms']:
            sms_info = SmsModel.objects(phone=request.phone).first()
            if sms_info and sms_info.code == request.smscode and (int(time.time())-sms_info.time <= 300):
                flag = True
                sms_info.delete()
        else:
            flag = True
        if flag and len(request.phone) > 0 and len(request.ownerpubkey) == 53 and len(request.actpubkey) == 53:
            m = RegisterReply()
            en_phone = None
            authkey = None
            nickname = ""
            if hasattr(request, "phoneEncrypt"):
                en_phone = request.phoneEncrypt
            if hasattr(request, "authkey"):
                authkey = request.authkey
            if hasattr(request, "nickname"):
                nickname = request.nickname
            user_info, referral = self._register(request.phone, en_phone, request.ownerpubkey, request.actpubkey, request.referral, authkey, nickname)
            #print(user_info)
            if user_info and "status" in user_info:
                if "uid" in user_info:
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
            return RegisterReply(code=2,msg="Invalid verification code") 
        
    def Follow(self, request, context):
        if request.user and request.follower:
            f = FollowModel()
            u = UserModel.objects(userid=request.user).first()
            fu = UserModel.objects(userid=request.follower).first()
            if u and fu:
                f.user = u
                f.follower = fu
                f.save()
                return BaseReply(msg="success")
        return BaseReply(code=3,msg="Invalid paras") 
            


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