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
import requests
import hashlib
import urllib

from center.rpc.bitsflea_pb2_grpc import add_BitsFleaServicer_to_server, BitsFleaServicer
from center.rpc.bitsflea_pb2 import RegisterRequest, User, BaseReply, PayInfo, Config
from center.rpc.bitsflea_pb2 import SearchRequest
from center.rpc.bitsflea_pb2 import FollowRequest
from center.rpc.bitsflea_pb2 import RefreshTokenRequest
from center.rpc.google.protobuf.wrappers_pb2 import StringValue

from center.gateway import Gateway
from center.utils import Utils
from center.eoslib.signature import verify_message
from center.eoslib.keys import PublicKey

from binascii import unhexlify, hexlify

import mongoengine

from center.database.schema import schema
from center.database.model import Follow as FollowModel
from center.database.model import Sms as SmsModel
from center.database.model import User as UserModel
from center.database.model import Product as ProductModel
from center.database.model import Favorite as FavoriteModel
from center.database.model import ReceiptAddress as ReceiptAddressModel
from center.database.model import Tokens as TokensModel

import ipfshttpclient as IPFS
from eospy.cleos import Cleos
from eospy.types import PackedTransaction


class Server(BitsFleaServicer):
    def __init__(self, config):
        self.logger = Logger()
        self.config = config
        self._connectDB(self.config['mongo'])
        self.gateway = Gateway(self.config['gateway'], self.logger)
        self.eosapi = Cleos(self.config['sync_cfg']['api_url'])
        try:
            self.ipfs_client = IPFS.connect(self.config['ipfs_api'])
        except Exception as e:
            print("IPFS ConnectionError:", e)

    def _connectDB(self, config):
        # 连接mongoengine
        mongoengine.connect(db=config['db'], host=config['host'], port=config['port'])

    def SendSmsCode(self, request, context):
        is_phone = re.match(r"^1[3456789]\d{9}$", request.phone)
        if is_phone:
            code = "".join(random.sample('0123456789', 6))
            try:
                result = self._xsendRegSMS(request.phone, code)
                if result:
                    sms = SmsModel.objects(phone=request.phone).first()
                    if sms:
                        sms.code = code
                        sms.time = int(time.time())
                        sms.save()
                    else:
                        SmsModel(phone=request.phone, code=code, time=int(time.time())).save()
                    return BaseReply(code=0, msg="success")
            except Exception as e:
                self.logger.Error("SendSmsCode error: ", e)
                return BaseReply(code=3004, msg="message failed to send")
        return BaseReply(code=3001, msg="Phone numbers not currently supported")

    def _xsendRegSMS(self, phone, code):
        project = self.config['sms']['projects']['reg']
        api_url = self.config['sms']['svr_url']
        app_id = self.config['sms']['appid']
        app_key = self.config['sms']['appkey']
        sms_vars = json.dumps({"code": code, "time": "120秒"})
        data = {'appid': app_id, 'project': project, 'sign_type': "sha1", 'timestamp': str(int(time.time())), 'to': phone}  #'sign_version': "2",
        query = urllib.parse.urlencode(data)
        query = "{}{}{}&vars={}{}{}".format(app_id, app_key, query, sms_vars, app_id, app_key)
        signature = hashlib.sha1(query.encode('utf-8')).hexdigest()
        data['vars'] = sms_vars
        data["signature"] = signature
        res = requests.post(api_url, json=data, headers={'Content-Type': "application/json"})
        if res.status_code == 200:
            result = res.json()
            if result['status'] == "success":
                return True
        return False

    def RefreshToken(self, request, context):
        from center.rpc.google.protobuf.any_pb2 import Any
        token = "0"
        if request.token and request.token != "0":
            token = request.token
        user = UserModel.objects(phone=request.phone).first()
        if user:
            # 验证
            msg = "{}{}{}".format(request.phone, token, request.time)
            #phex = verify_message(msg, unhexlify(request.sign))
            phex = verify_message(msg, request.sign)
            authKey = str(PublicKey(hexlify(phex).decode("ascii")))
            br = BaseReply()
            #print("RefreshToken: ", user.authKey, authKey)
            if user.authKey == authKey:
                code = "".join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz', 16))
                tm = TokensModel.objects(phone=request.phone).first()
                if tm:
                    exp = int(time.time()) - tm.expiration
                    if exp >= 3600 or exp >= 86400:
                        tm.userid = user.userid
                        tm.token = Utils.sha256(bytes(code, "utf8"))
                        tm.expiration = int(time.time() + 86400)
                        tm.save()
                else:
                    tm = TokensModel()
                    tm.userid = user.userid
                    tm.phone = request.phone
                    tm.token = Utils.sha256(bytes(code, "utf8"))
                    tm.expiration = int(time.time() + 86400)
                    tm.save()
                br.msg = "success"
                br.data.Pack(StringValue(value=tm.token))
                return br
            else:
                return BaseReply(code=3002, msg="Invalid signature")
        return BaseReply(code=1, msg="Invalid parameter")

    def Search(self, request, context):
        #print( context.invocation_metadata())
        sur = BaseReply()
        if request.query:
            result = schema.execute(request.query)
            if result.data:
                sur.msg = "success"
                sur.data.Pack(StringValue(value=json.dumps(result.data)))
            else:
                sur.code = 400
                sur.msg = "no data"
        else:
            sur.code = 1
            sur.msg = "Invalid parameter"
        return sur

    def Transaction(self, request, context):
        # print("request:",request)
        if request.trx:
            sign = True if request.sign else False
            if sign:
                tmp_trx = json.loads(request.trx)
                if "transaction" in tmp_trx:
                    tmp_trx = tmp_trx['transaction']
                elif "packed_trx" in tmp_trx:
                    # print(tmp_trx)
                    p_Trx = PackedTransaction(tmp_trx['packed_trx'], self.eosapi)
                    tmp_trx = p_Trx.get_transaction()
                    # print(json.dumps(tmp_trx))
                else:
                    return BaseReply(code=1, msg="Invalid parameter")
                if len(tmp_trx['actions']) != 1 or tmp_trx['actions'][0]['account'] != self.config['sync_cfg']['contract'] or (
                        tmp_trx['actions'][0]['name'] not in self.config['sgin_actions']):
                    return BaseReply(code=401, msg="This action has no permissions")
            result = None
            try:
                result = self.gateway.broadcast(request.trx, sign=sign)
            except Exception as e:
                self.logger.Error("gateway error: ", e=e, screen=True)
            if result and result['status'] == "success":
                return BaseReply(code=0, msg="success")
            else:
                return BaseReply(code=500, msg=result['message'])
        return BaseReply(code=1, msg="Invalid parameter")

    def _register(self, phone, en_phone, owner, active, authkey, referral, nickname):
        user = None
        # 获取引荐人
        (referral, referral_name) = self.gateway.getReferral(eosid=referral)
        #print("ref: ", ref)
        if not referral or not referral_name:
            referral = int(self.config['referrer'][0])
            referral_name = self.config['referrer'][1]
        # authkey
        if not authkey or len(authkey) != len(active):
            authkey = active
        # 处理手机号
        phone_hash = Utils.sha256(bytes(phone, "utf8"))
        #print("phone_hash: ", phone_hash)
        if not en_phone:
            en_phone = Utils.encrypt_phone(phone, authkey, self.config['encrypt_key'])
        # 创建eos id
        result = None
        try:
            result = self.gateway.createAccount(nickname, owner, active, authkey, referral, phone_hash, en_phone)
        except Exception as e:
            self.logger.Error("gateway error: ", e=e, screen=True)
        # print(result)
        if result:
            if result['status'] == "success":
                # 获取注册信息
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
            if sms_info and sms_info.code == request.smscode and (int(time.time()) - sms_info.time <= 300):
                flag = True
                sms_info.delete()
        else:
            flag = True
        m = BaseReply()
        if flag and len(request.phone) > 0 and len(request.ownerpubkey) == 53 and len(request.actpubkey) == 53:
            en_phone = None
            authkey = None
            nickname = ""
            if hasattr(request, "phoneEncrypt"):
                en_phone = request.phoneEncrypt
            if hasattr(request, "authkey"):
                authkey = request.authkey
            if hasattr(request, "nickname"):
                nickname = request.nickname
            user_info, referral = self._register(request.phone, en_phone, request.ownerpubkey, request.actpubkey, authkey, request.referral, nickname)
            # print(user_info)
            if user_info and "status" in user_info:
                if "uid" in user_info:
                    m.msg = "registration successful"
                    user = User()
                    user.userid = user_info['uid']
                    user.eosid = user_info['eosid']
                    user.phone = request.phone  # user_info['phone_encrypt']
                    user.status = user_info['status']
                    user.nickname = user_info['nickname']
                    user.creditValue = user_info['credit_value']
                    user.referrer = referral  # str(user_info['referrer'])
                    user.lastActiveTime = user_info['last_active_time']
                    user.postsTotal = user_info['posts_total']
                    user.sellTotal = user_info['sell_total']
                    user.buyTotal = user_info['buy_total']
                    user.referralTotal = user_info['referral_total']
                    user.point = user_info['point']
                    user.isReviewer = user_info['is_reviewer']
                    user.authKey = authkey
                    m.data.Pack(user)
                    um = UserModel()
                    um.authKey = user.authKey
                    um.userid = user.userid
                    um.eosid = user.eosid
                    um.phone = user.phone
                    um.status = user.status
                    um.nickname = user.nickname
                    um.head = user.head
                    um.creditValue = user.creditValue
                    um.referrer = user.referrer
                    um.lastActiveTime = user.lastActiveTime
                    um.referralTotal = user.referralTotal
                    um.point = user.point
                    um.isReviewer = user.isReviewer
                    um.save()
                else:
                    m.code = 101
                    m.msg = user_info['message']
            else:
                m.code = 500
                m.msg = "An error occurred while requesting the gateway"
            return m
        else:
            m.code = 1
            m.msg = "Invalid parameter"
            return m

    def _check_auth(self, userid, metadata):
        token = dict(metadata)['token']
        tm = TokensModel.objects(token=token).first()
        if tm and tm.userid == userid:
            return True
        return False

    def Follow(self, request, context):
        if self._check_auth(request.follower, context.invocation_metadata()) == False:
            return BaseReply(code=2, msg="Access denied")
        if request.user and request.follower:
            f = FollowModel()
            u = UserModel.objects(userid=request.user).first()
            fu = UserModel.objects(userid=request.follower).first()
            if u and fu:
                f.user = u
                f.follower = fu
                f.save()
                u.fansTotal += 1
                u.save()
                fu.followTotal += 1
                fu.save()
                return BaseReply(msg="success")
        return BaseReply(code=1, msg="Invalid parameter")

    def UnFollow(self, request, context):
        if self._check_auth(request.follower, context.invocation_metadata()) == False:
            return BaseReply(code=2, msg="Access denied")
        if request.user and request.follower:
            f = FollowModel.objects(user=request.user, follower=request.follower).first()
            if f:
                u = UserModel.objects(userid=request.user).first()
                if u.fansTotal > 0:
                    u.fansTotal -= 1
                u.save()
                fu = UserModel.objects(userid=request.follower).first()
                if fu.followTotal > 0:
                    fu.followTotal -= 1
                fu.save()
                f.delete()
                return BaseReply(msg="success")
        return BaseReply(code=1, msg="Invalid parameter")

    def Favorite(self, request, context):
        if self._check_auth(request.user, context.invocation_metadata()) == False:
            return BaseReply(code=2, msg="Access denied")
        if request.user and request.product:
            u = UserModel.objects(userid=request.user).first()
            p = ProductModel.objects(productId=request.product).first()
            if u and p:
                c = FavoriteModel()
                c.user = u
                c.product = p
                c.save()
                u.favoriteTotal += 1
                u.save()
                p.collections += 1
                p.save()
                return BaseReply(msg="success")
        return BaseReply(code=1, msg="Invalid parameter")

    def UnFavorite(self, request, context):
        if self._check_auth(request.user, context.invocation_metadata()) == False:
            return BaseReply(code=2, msg="Access denied")
        if request.user and request.product:
            c = FavoriteModel.objects(user=request.user, product=request.product).first()
            p = ProductModel.objects(productId=request.product).first()
            if c:
                if p.collections > 0:
                    p.collections -= 1
                p.save()
                u = UserModel.objects(userid=request.user).first()
                if u.favoriteTotal > 0:
                    u.favoriteTotal -= 1
                u.save()
                c.delete()

                return BaseReply(msg="success")
        return BaseReply(code=1, msg="Invalid parameter")

    def Address(self, request, context):
        if self._check_auth(request.userid, context.invocation_metadata()) == False:
            return BaseReply(code=2, msg="Access denied")
        if request.userid:
            u = UserModel.objects(userid=request.userid).first()
            if u:
                r = ReceiptAddressModel()
                r.userid = request.userid
                r.province = request.province
                r.city = request.city
                r.district = request.district
                r.phone = request.phone
                r.name = request.name
                r.address = request.address
                r.postcode = request.postcode
                r.isDefault = request.isDefault
                r.save()
                return BaseReply(msg="success")
        return BaseReply(code=1, msg="Invalid parameter")

    def UpdateAddress(self, request, context):
        if self._check_auth(request.userid, context.invocation_metadata()) == False:
            return BaseReply(code=2, msg="Access denied")
        if request.rid and request.userid:
            r = ReceiptAddressModel.objects(rid=request.rid).first()
            u = UserModel.objects(userid=request.userid).first()
            if r and u:
                r.province = request.province
                r.city = request.city
                r.district = request.district
                r.phone = request.phone
                r.name = request.name
                r.address = request.address
                r.postcode = request.postcode
                r.isDefault = request.isDefault
                r.save()
                return BaseReply(msg="success")
        return BaseReply(code=1, msg="Invalid parameter")

    def SetDefaultAddr(self, request, context):
        if self._check_auth(request.userid, context.invocation_metadata()) == False:
            return BaseReply(code=2, msg="Access denied")
        if request.rid and request.userid:
            r = ReceiptAddressModel.objects(rid=request.rid).first()
            if r and r.userid == request.userid:
                ReceiptAddressModel.objects(userid=request.userid).update(isDefault=False)
                r.isDefault = True
                r.save()
                return BaseReply(msg="success")
        return BaseReply(code=1, msg="Invalid parameter")

    def DelAddress(self, request, context):
        if self._check_auth(request.userid, context.invocation_metadata()) == False:
            return BaseReply(code=2, msg="Access denied")
        if request.rid:
            r = ReceiptAddressModel.objects(rid=request.rid).first()
            if r:
                r.delete()
                return BaseReply(msg="success")
        return BaseReply(code=1, msg="Invalid parameter")

    def Upload(self, request, context):
        #file = bytes(request.file)
        #client = IPFS.connect(self.config['ipfs_api'])
        if request.file:
            res = self.ipfs_client.add_bytes(request.file)
            return BaseReply(msg=res)
        else:
            return BaseReply(code=1, msg="Invalid parameter")

    def CreatePayInfo(self, request, context):
        if self._check_auth(request.userId, context.invocation_metadata()) == False:
            return BaseReply(code=2, msg="Access denied")
        if request.userId and request.productId and request.amount and request.symbol:
            if not request.orderid:
                # create order id
                orderid = str(((request.userId << 64) | (request.productId << 32)) | int(time.time()))
            else:
                orderid = request.orderid
            # get pay address
            addr = {}
            if request.mainPay:
                addr['address'] = self.config['sync_cfg']['contract']
                addr['chain'] = "bos"
            else:
                addr = self.gateway.createAddress(orderid, request.symbol)
            if not addr['address']:
                # bosibc支付,直接跨链向主合约发起支付
                addr['address'] = self.config['sync_cfg']['contract']
            pay_info = PayInfo()
            pay_info.orderid = orderid
            pay_info.amount = request.amount
            pay_info.symbol = request.symbol
            pay_info.payAddr = addr['address']
            pay_info.userId = request.userId
            pay_info.productId = request.productId
            pay_info.payMode = 0 if request.mainPay else 1
            pay_info.chain = addr['chain']
            if "precision" in addr:
                pay_info.precision = addr['precision']
            if "coin_address" in addr:
                pay_info.coinAddr = addr['coin_address']
            br = BaseReply(msg="success")
            br.data.Pack(pay_info)
            return br
        return BaseReply(code=1, msg="Invalid parameter")

    def LogisticsInfo(self, request, context):
        if self._check_auth(request.userId, context.invocation_metadata()) == False:
            return BaseReply(code=2, msg="Access denied")
        if request.number:
            com = request.com if request.com else "AUTO"
            try:
                headers = {'Authorization': 'APPCODE ' + self.config['logistics_api_key']}
                number = request.number
                if number[0:2] == "SF":
                    fromUser = UserModel.objects(userid=request.userId).first()
                    if fromUser:
                        number = "{}:{}".format(request.number, fromUser.phone[-4:])
                html = requests.get(self.config['logistics_api'], headers=headers, data={'type': com, 'no': number})
                if html.status_code == 200:
                    return BaseReply(msg=html.text)
                return BaseReply(code=3003, msg="search logistics info error")
            except Exception as e:
                self.logger.Error("get logistics info error:", e=e, screen=True)
                return BaseReply(code=3003, msg="get logistics info error")
        return BaseReply(code=1, msg="Invalid parameter")

    def GetPhone(self, request, context):
        if self._check_auth(request.fromUserId, context.invocation_metadata()) == False:
            return BaseReply(code=2, msg="Access denied")
        if request.toUserId:
            toUser = UserModel.objects(userid=request.toUserId).first()
            if toUser:
                return BaseReply(msg="{}".format(toUser.phone))
        return BaseReply(code=1, msg="Invalid parameter")

    def GetConfig(self, request, context):
        config = Config()
        config.mainContract = self.config['sync_cfg']['contract']
        config.eosAPI = self.config['sync_cfg']['api_url']
        config.ipfsGateway = self.config['client']['ipfs_gateway']
        config.mainTokenContract = self.config['client']['main_token_contract']
        config.eosTokenContract = self.config['client']['eos_token_contract']
        config.bosIBCContract = self.config['client']['ibc_token_contract']
        config.mainAssetSymbol = self.config['client']['main_asset_symbol']
        config.amapDistrictKey = self.config['client']['amap_district_key']
        config.showCNY = self.config['client']['show_cny']
        br = BaseReply(msg="success")
        br.data.Pack(config)
        return br

    def closeIPFS(self):
        if self.ipfs_client:
            self.ipfs_client.close()


class TokenInterceptor(grpc.ServerInterceptor):
    def __init__(self):
        def abort(ignored_request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, 'Invalid token')

        self._abortion = grpc.unary_unary_rpc_method_handler(abort)

    def intercept_service(self, continuation, handler_call_details):
        method_name = handler_call_details.method.split('/')
        meta = dict(handler_call_details.invocation_metadata)
        # print(meta)
        token = ""
        if "token" in meta:
            token = meta['token']
        flag = False
        tm = TokensModel.objects(token=token).first()
        allows = ['RefreshToken', 'SendSmsCode', 'Register', 'Search', 'GetConfig']
        if method_name[-1] in allows or (tm and (int(time.time()) - tm.expiration) <= 86400):
            flag = True
        if tm and flag == False:
            tm.delete()
        if flag:
            return continuation(handler_call_details)
        else:
            return self._abortion


def bits_flea_run(config):
    # 这里通过thread pool来并发处理server的任务
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors=(TokenInterceptor(), ))

    # 将对应的任务处理函数添加到rpc server中
    fleaSvr = Server(config)
    add_BitsFleaServicer_to_server(fleaSvr, server)

    # 这里使用的非安全接口，世界gRPC支持TLS/SSL安全连接，以及各种鉴权机制
    port = "[::]:{}".format(config['server_port'])
    print("start {}".format(port))
    server.add_insecure_port(port)
    server.start()
    try:
        while True:
            time.sleep(60 * 60 * 24)
    except KeyboardInterrupt:
        fleaSvr.closeIPFS()
        server.stop(0)
