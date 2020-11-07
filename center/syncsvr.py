import asyncio
import aiohttp
import mongoengine
import json as JSON
import time

from mongoengine.queryset.visitor import Q

from center.utils import Utils
from center.gateway import Gateway
from center.logger import Logger
from center.database.model import TableLog as TableLogModel
from center.database.model import User as UserModel
from center.database.model import Category as CategoryModel
from center.database.model import Reviewer as ReviewerModel
from center.database.model import Product as ProductModel
from center.database.model import Auction as AuctionModel
from center.database.model import ProductAudit as ProductAuditModel
from center.database.model import Order as OrderModel
from center.database.model import ProReturn as ProReturnModel
from center.database.model import Arbitration as ArbitrationModel
from center.database.model import OtherAddr as OtherAddrModel

from eospy.utils import decimalToBinary, binaryToDecimal


class SyncSvr:
    def __init__(self, config, get_init=False):
        self.logger = Logger("sync")
        self.config = config['sync_cfg']
        self.db_config = config['mongo']
        self.public_config = config
        self.get_init = get_init
        self._init_db()
        self.gateway = Gateway(config['gateway'], self.logger)
        self.retry_times = {}

    def _init_db(self):
        #连接mongoengine
        mongoengine.connect(db=self.db_config['db'], host=self.db_config['host'], port=self.db_config['port'])

    def _deleteLogs(self, tid):
        payload = {
            "account": self.config['contract'],
            "name": "deletelog",
            "authorization": [{
                "actor": self.config['contract'],
                "permission": "active",
            }],
            "data": {
                "id": tid
            }
        }
        trx = {"transaction": {"actions": [payload]}}
        result = self.gateway.broadcast(trx, sign=True)
        if result['status'] == "success":
            print("The chain log of [{}] has been deleted".format(tid))
        else:
            self.logger.Error("Failed to delete logs on the chain", None, result, screen=True)

    async def _post(self, data=None, json=None, uri="get_table_rows"):
        result = None
        url = self.config['api_url']
        url = "{}{}{}".format(url, ("v1/chain/" if url.endswith("/") else "/v1/chain/"), uri)
        tkey = Utils.sha256(("{}{}{}".format(url, JSON.dumps(data),JSON.dumps(json))).encode())
        # print("tkey: ",tkey)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data, json=json) as response:
                    if response.status == 200 or response.status == 202:
                        result = await response.json()
                        self.retry_times.pop(tkey, 0)
            except Exception as e:
                self.logger.Error("post error: {}".format(url), e=e, screen=True)
                times = 1
                if self.retry_times.has_key(tkey):
                    times = self.retry_times[tkey] + 1
                    self.retry_times[tkey] = times
                else:
                    self.retry_times[tkey] = times
                if times < self.config['retry_max']:
                    self.logger.Error("post retry: {}".format(url), screen=True)
                    await asyncio.sleep(1)
                    result = await self._post(data, json, uri)
                else:
                    del self.retry_times[tkey]
                    self.logger.Error("post retry failure: {}".format(url), screen=True)
        return result

    def getIncrementTasks(self, loop):
        tasks = [
            loop.create_task(self.taskSyncTableLog()),
            loop.create_task(self.taskSyncUser()),
            loop.create_task(self.taskSyncOtherAddr()),
            loop.create_task(self.taskSyncReviewer()),
            loop.create_task(self.taskSyncProduct()),
            loop.create_task(self.taskSyncAuction()),
            loop.create_task(self.taskSyncAudit()),
            loop.create_task(self.taskSyncOrder()),
            loop.create_task(self.taskSyncReturn()),
            loop.create_task(self.taskSyncArbitration()),
            loop.create_task(self.taskSyncCategory())
        ]
        return tasks

    def getInitTasks(self, loop):
        tasks = []

        # users
        async def syncUser(userid=0, limit=50):
            try:
                id, more = await self.getUsers(userid, limit)
                while (more):
                    id, more = await self.getUsers(id, limit)
                print("[{}]Sync to user id:{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), id))
            except KeyboardInterrupt as ke:
                print("init users sync stop...")

        tasks.append(loop.create_task(syncUser()))

        #Categories
        async def syncCategory(cid=0, limit=50):
            try:
                id, more = await self.getCategories(cid, limit=limit)
                while (more):
                    id, more = await self.getCategories(id, limit=limit)
                print("Sync to category id:{}".format(id))
            except KeyboardInterrupt as ke:
                print("init categories sync stop...")

        tasks.append(loop.create_task(syncCategory()))

        #Reviewers
        async def syncReviewer(uid=0, limit=50):
            try:
                id, more = await self.getReviewers(uid, limit=limit)
                while (more):
                    id, more = await self.getReviewers(id, limit=limit)
                print("Sync to reviewer id:{}".format(id))
            except KeyboardInterrupt as ke:
                print("init reviewers sync stop...")

        tasks.append(loop.create_task(syncReviewer()))

        #products
        async def syncProduct(pid=0, limit=50):
            try:
                id, more = await self.getProducts(pid, limit=limit)
                while (more):
                    id, more = await self.getProducts(id, limit=limit)
                print("Sync to product id:{}".format(id))
            except KeyboardInterrupt as ke:
                print("init products sync stop...")

        tasks.append(loop.create_task(syncProduct()))

        #Auctions
        async def syncAuction(pid=0, limit=50):
            try:
                id, more = await self.getAuctions(pid, limit=limit)
                while (more):
                    id, more = await self.getAuctions(id, limit=limit)
                print("Sync to auction id:{}".format(id))
            except KeyboardInterrupt as ke:
                print("init auctions sync stop...")

        tasks.append(loop.create_task(syncAuction()))

        #ProductAudits
        async def syncProductAudit(pid=0, limit=50):
            try:
                id, more = await self.getAudits(pid, limit=limit)
                while (more):
                    id, more = await self.getAudits(id, limit=limit)
                print("Sync to audit id:{}".format(id))
            except KeyboardInterrupt as ke:
                print("init ProductAudits sync stop...")

        tasks.append(loop.create_task(syncProductAudit()))

        #Orders
        async def syncOrder(oid=0, limit=50):
            try:
                id, more = await self.getOrders(int(oid), limit=limit)
                while (more):
                    id, more = await self.getOrders(id, limit=limit)
                print("Sync to order id:{}".format(id))
            except KeyboardInterrupt as ke:
                print("init orders sync stop...")

        tasks.append(loop.create_task(syncOrder()))

        #ProReturns
        async def syncProReturn(oid=0, limit=50):
            try:
                id, more = await self.getReturns(oid, limit=limit)
                while (more):
                    id, more = await self.getReturns(id, limit=limit)
                print("Sync to return id:{}".format(id))
            except KeyboardInterrupt as ke:
                print("init returns sync stop...")

        tasks.append(loop.create_task(syncProReturn()))

        #Arbitrations
        async def syncArbitration(aid=0, limit=50):
            try:
                id, more = await self.getArbitrations(aid, limit=limit)
                while (more):
                    id, more = await self.getArbitrations(id, limit=limit)
                print("Sync to arbitration id:{}".format(id))
            except KeyboardInterrupt as ke:
                print("init arbitrations sync stop...")

        tasks.append(loop.create_task(syncArbitration()))

        #OtherAddrs
        async def syncOtherAddr(oaid=0, limit=50):
            try:
                id, more = await self.getOtherAddrs(oaid, limit=limit)
                while (more):
                    id, more = await self.getOtherAddrs(id, limit=limit)
                print("Sync to otheraddr id:{}".format(id))
            except KeyboardInterrupt as ke:
                print("init otheraddr sync stop...")

        tasks.append(loop.create_task(syncOtherAddr()))

        return tasks

    def Run(self):
        loop = asyncio.get_event_loop()
        try:
            if self.get_init:
                print("init data...")
                loop.run_until_complete(asyncio.wait(self.getInitTasks(loop)))
                print("init data complete.")
            print("Start incremental sync...")
            loop.run_until_complete(asyncio.wait(self.getIncrementTasks(loop)))
            loop.close()
        except KeyboardInterrupt as ke:
            print("sync server stop.")

    #   incremental sync task

    async def taskSyncTableLog(self):
        try:
            while (True):
                tid, more = await self.getTableLogs(0)
                while (more):
                    tid, more = await self.getTableLogs(tid)
                    await asyncio.sleep(2)
                if tid > 0:
                    self._deleteLogs(tid)
                await asyncio.sleep(self.config['sync_log_interval'])
        except KeyboardInterrupt as ke:
            print("tablelog sync stop...")

    async def taskSyncUser(self):
        try:
            while (True):
                logs = TableLogModel.objects(table="users").limit(50)
                id = 0
                more = False
                for log in logs:
                    id, more = await self.getUsers(userid=int(log.primary), limit=1)
                    log.delete()
                if id > 0:
                    print("[{}]Sync to user id:{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), id))
                await asyncio.sleep(5)
        except KeyboardInterrupt as ke:
            print("users incremental sync stop...")

    async def taskSyncCategory(self):
        try:
            while (True):
                logs = TableLogModel.objects(table="categories").limit(50)
                for log in logs:
                    await self.getCategories(cid=int(log.primary), limit=1)
                    log.delete()
                await asyncio.sleep(5)
        except KeyboardInterrupt as ke:
            print("categories incremental sync stop...")

    async def taskSyncReviewer(self):
        try:
            while (True):
                logs = TableLogModel.objects(table="reviewers").limit(50)
                for log in logs:
                    await self.getReviewers(uid=int(log.primary), limit=1)
                    log.delete()
                await asyncio.sleep(5)
        except KeyboardInterrupt as ke:
            print("reviewers incremental sync stop...")

    async def taskSyncProduct(self):
        try:
            while (True):
                logs = TableLogModel.objects(table="products").limit(50)
                for log in logs:
                    await self.getProducts(pid=int(log.primary), limit=1)
                    log.delete()
                await asyncio.sleep(5)
        except KeyboardInterrupt as ke:
            print("products incremental sync stop...")

    async def taskSyncAuction(self):
        try:
            while (True):
                logs = TableLogModel.objects(table="proauction").limit(50)
                for log in logs:
                    await self.getAuctions(pid=int(log.primary), limit=1)
                    log.delete()
                await asyncio.sleep(5)
        except KeyboardInterrupt as ke:
            print("proauction incremental sync stop...")

    async def taskSyncAudit(self):
        try:
            while (True):
                logs = TableLogModel.objects(table="proaudits").limit(50)
                for log in logs:
                    await self.getAudits(pid=int(log.primary), limit=1)
                    log.delete()
                await asyncio.sleep(5)
        except KeyboardInterrupt as ke:
            print("proaudits incremental sync stop...")

    async def taskSyncOrder(self):
        try:
            while (True):
                logs = TableLogModel.objects(table="orders").limit(50)
                oid = 0
                for log in logs:
                    oid = int(log.primary)
                    if log.ttype == 1:
                        OrderModel.objects(oid=oid).delete()
                    else:
                        await self.getOrders(oid=oid, limit=1)
                    log.delete()
                if oid > 0:
                    print("[{}]Sync to order id: {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), oid))
                await asyncio.sleep(5)
        except KeyboardInterrupt as ke:
            print("orders incremental sync stop...")

    async def taskSyncReturn(self):
        try:
            while (True):
                logs = TableLogModel.objects(table="returns").limit(50)
                for log in logs:
                    await self.getReturns(oid=log.primary, limit=1)
                    log.delete()
                await asyncio.sleep(5)
        except KeyboardInterrupt as ke:
            print("returns incremental sync stop...")

    async def taskSyncArbitration(self):
        try:
            while (True):
                logs = TableLogModel.objects(table="arbitrations").limit(50)
                for log in logs:
                    await self.getArbitrations(aid=int(log.primary), limit=1)
                    log.delete()
                await asyncio.sleep(5)
        except KeyboardInterrupt as ke:
            print("arbitrations incremental sync stop...")

    async def taskSyncOtherAddr(self):
        try:
            while (True):
                logs = TableLogModel.objects(table="otheraddr").limit(50)
                for log in logs:
                    await self.getOtherAddrs(oaid=int(log.primary), limit=1)
                    log.delete()
                await asyncio.sleep(5)
        except KeyboardInterrupt as ke:
            print("otheraddr incremental sync stop...")

    #   incremental sync task end

    # pull data methods

    async def getTableLogs(self, id=0, limit=50):
        data = {"code": self.config['contract'], "scope": self.config['contract'], "table": "tablelogs", "lower_bound": id, "limit": limit, "json": True}
        tid = id
        result = await self._post(json=data)
        if result and len(result['rows']) > 0:
            for log in result['rows']:
                l = TableLogModel.objects(Q(table=log['table']) & Q(primary=log['primary'])).first()
                if not l:
                    l = TableLogModel(tid=log['id'])
                    l.table = log['table']
                    l.ttype = log['type']
                    l.primary = log['primary']
                    l.save()
                tid = log['id']
        return tid, result['more']

    async def getUsers(self, userid=0, limit=50):
        data = {
            "code": self.config['contract'],
            "scope": self.config['contract'],
            "table": "users",
            #"index_position":2,
            #"key_type":"i64",
            "lower_bound": userid,
            "limit": limit,
            "json": True
        }
        uid = userid
        result = await self._post(json=data)
        if result and len(result['rows']) > 0:
            for user in result['rows']:
                u = UserModel(userid=user['uid'])
                u.eosid = user['eosid']
                u.authKey = user['auth_key']
                phone = user['phone_encrypt']
                if phone.startswith("05FBED483A974456708") == False:
                    phone = Utils.decrypt_phone(phone, u.authKey, self.public_config['encrypt_key'])
                u.phone = phone
                u.status = user['status']
                u.nickname = user['nickname']
                u.head = user['head']
                u.creditValue = user['credit_value']
                u.referrer = str(user['referrer'])
                u.lastActiveTime = user['last_active_time']
                u.postsTotal = user['posts_total']
                u.sellTotal = user['sell_total']
                u.buyTotal = user['buy_total']
                u.referralTotal = user['referral_total']
                u.point = user['point']
                u.isReviewer = user['is_reviewer'] > 0
                u.save()
                uid = u.userid
            if uid == userid and result['more']:
                uid += 1
            return uid, result['more']
        return uid, False

    async def getCategories(self, cid=0, limit=50):
        data = {"code": self.config['contract'], "scope": self.config['contract'], "table": "categories", "lower_bound": cid, "limit": limit, "json": True}
        result = await self._post(json=data)
        id = cid
        if result and len(result['rows']) > 0:
            for cate in result['rows']:
                c = CategoryModel(cid=cate['id'])
                c.view = cate['view']
                c.parent = cate['parent']
                c.save()
                id = c.cid
            if result['more'] and id == cid:
                id += 1
            return id, result['more']
        return id, False

    async def getReviewers(self, uid=0, limit=50):
        data = {"code": self.config['contract'], "scope": self.config['contract'], "table": "reviewers", "lower_bound": uid, "limit": limit, "json": True}
        result = await self._post(json=data)
        id = uid
        if result and len(result['rows']) > 0:
            for reviewer in result['rows']:
                r = ReviewerModel(rid=reviewer['id'])
                #r.userid = reviewer['uid']
                r.eosid = reviewer['eosid']
                r.votedCount = reviewer['voted_count']
                r.createTime = reviewer['create_time']
                r.lastActiveTime = reviewer['last_active_time']
                r.voterApprove = reviewer['voter_approve']
                r.voterAgainst = reviewer['voter_against']
                user = UserModel.objects(userid=reviewer['uid']).first()
                if user is None:
                    await self.getUsers(reviewer['uid'], 1)
                    user = UserModel.objects(userid=reviewer['uid']).first()
                r.user = user
                r.save()
                id = r.user.userid
            if result['more'] and id == uid:
                id += 1
            return id, result['more']
        return id, False

    async def getProducts(self, pid=0, limit=50):
        data = {"code": self.config['contract'], "scope": self.config['contract'], "table": "products", "lower_bound": pid, "limit": limit, "json": True}
        result = await self._post(json=data)
        id = pid
        if result and len(result['rows']) > 0:
            for product in result['rows']:
                p = ProductModel(productId=product['pid'])
                p.title = product['title']
                p.status = product['status']
                p.isNew = product['is_new'] > 0
                p.isReturns = product['is_returns'] > 0
                p.transMethod = product['transaction_method']
                p.postage = product['postage']
                p.position = product['position']
                p.releaseTime = product['release_time']
                p.description = product['description']
                p.photos = product['photos']
                p.price = product['price']
                p.saleMethod = product['sale_method']
                p.stockCount = product['stock_count']
                p.isRetail = product['is_retail'] != 0
                category = CategoryModel.objects(cid=product['category']).first()
                if not category:
                    await self.getCategories(cid=product['category'], limit=1)
                    category = CategoryModel.objects(cid=product['category']).first()
                p.category = category
                us = UserModel.objects(userid=product['uid']).first()
                if not us:
                    await self.getUsers(userid=product['uid'], limit=1)
                    us = UserModel.objects(userid=product['uid']).first()
                p.seller = us
                # rev = ReviewerModel.objects(rid=product['reviewer']).first()
                # if not rev:
                #     await self.getReviewers(rid=product['reviewer'], limit=1)
                #     rev = ReviewerModel.objects(rid=product['reviewer']).first()
                # p.reviewer = rev
                p.save()
                id = p.productId
            if result['more'] and id == pid:
                id += 1
            return id, result['more']
        return id, False

    async def getAuctions(self, pid=0, limit=50):
        data = {"code": self.config['contract'], "scope": self.config['contract'], "table": "proauction", "lower_bound": pid, "limit": limit, "json": True}
        result = await self._post(json=data)
        id = pid
        if result and len(result['rows']) > 0:
            for auction in result['rows']:
                a = AuctionModel(aid=auction['id'])
                a.security = auction['security']
                a.markup = auction['markup']
                a.currentPrice = auction['current_price']
                a.auctionTimes = auction['auction_times']
                a.startTime = auction['start_time']
                a.endTime = auction['end_time']
                lpu = UserModel.objects(userid=auction['last_price_user']).first()
                if not lpu:
                    await self.getUsers(userid=auction['last_price_user'], limit=1)
                    lpu = UserModel.objects(userid=auction['last_price_user']).first()
                a.lastPriceUser = lpu
                product = ProductModel.objects(productId=auction['pid']).first()
                if not product:
                    await self.getProducts(pid=auction['pid'], limit=1)
                    product = ProductModel.objects(productId=auction['pid']).first()
                a.product = product
                a.save()
                id = a.product.productId
            if result['more'] and id == pid:
                id += 1
            return id, result['more']
        return id, False

    async def getAudits(self, pid=0, limit=50):
        data = {"code": self.config['contract'], "scope": self.config['contract'], "table": "proaudits", "lower_bound": pid, "limit": limit, "json": True}
        result = await self._post(json=data)
        id = pid
        if result and len(result['rows']) > 0:
            for audit in result['rows']:
                a = ProductAuditModel(paid=audit['id'])
                a.isDelisted = audit['is_delisted']
                a.reviewDetails = audit['review_details']
                a.reviewTime = audit['review_time']
                product = ProductModel.objects(productId=audit['pid']).first()
                if not product:
                    await self.getProducts(pid=audit['pid'], limit=1)
                    product = ProductModel.objects(productId=audit['pid']).first()
                a.product = product
                reviewer = ReviewerModel.objects(user=audit['reviewer_uid']).first()
                if not reviewer:
                    await self.getReviewers(uid=audit['reviewer_uid'], limit=1)
                    reviewer = ReviewerModel.objects(user=audit['reviewer_uid']).first()
                a.reviewer = reviewer
                a.save()
                id = a.product.productId
            if result['more'] and id == pid:
                id += 1
            return id, result['more']
        return id, False

    async def getOrders(self, oid=0, limit=50):
        # data = {"code": self.config['contract'], "scope": self.config['contract'], "table": "orders", "index_position":6, "key_type":"i128", "lower_bound": oid, "limit": limit, "json": True}
        data = {"code": self.config['contract'], "scope": self.config['contract'], "table": "orders", "lower_bound": oid, "limit": limit, "json": True}
        result = await self._post(json=data)
        id = int(oid)
        if result and len(result['rows']) > 0:
            for order in result['rows']:
                o = OrderModel(oid=int(order['id']))
                order_id_data = decimalToBinary(16, order['oid'])
                o.orderid = binaryToDecimal(order_id_data)
                o.status = order['status']
                o.price = order['price']
                o.postage = order['postage']
                o.shipNum = order['shipment_number']
                o.payAddr = order['pay_addr']
                o.createTime = order['create_time']
                o.payTime = order['pay_time']
                o.payOutTime = order['pay_time_out']
                o.shipTime = order['ship_time']
                o.shipOutTime = order['ship_time_out']
                o.receiptTime = order['receipt_time']
                o.receiptOutTime = order['receipt_time_out']
                o.endTime = order['end_time']
                o.delayedCount = order['delayed_count']
                o.toAddr = order['to_addr']
                product = ProductModel.objects(productId=order['pid']).first()
                if not product:
                    await self.getProducts(pid=order['pid'], limit=1)
                    product = ProductModel.objects(productId=order['pid']).first()
                o.productInfo = product
                seller = UserModel.objects(userid=order['seller_uid']).first()
                if not seller:
                    await self.getUsers(userid=order['seller_uid'], limit=1)
                    seller = UserModel.objects(userid=order['seller_uid']).first()
                o.seller = seller
                buyer = UserModel.objects(userid=order['buyer_uid']).first()
                if not buyer:
                    await self.getUsers(userid=order['buyer_uid'], limit=1)
                    buyer = UserModel.objects(userid=order['buyer_uid']).first()
                o.buyer = buyer
                o.save()
                id = int(o.oid)
            if result['more'] and id == oid:
                id += 1
            return id, result['more']
        return id, False

    async def getReturns(self, oid=0, limit=50):
        data = {"code": self.config['contract'], "scope": self.config['contract'], "table": "returns", "lower_bound": oid, "limit": limit, "json": True}
        result = await self._post(json=data)
        id = oid
        if result and len(result['rows']) > 0:
            for pro in result['rows']:
                pr = ProReturnModel(prid=pro['id'])
                pr.orderPrice = pro['order_price']
                pr.status = pro['status']
                pr.reasons = pro['reasons']
                pr.createTime = pro['create_time']
                pr.shipNum = pro['shipment_number']
                pr.shipTime = pro['ship_time']
                pr.shipOutTime = pro['ship_time_out']
                pr.receiptTime = pro['receipt_time']
                pr.receiptOutTime = pro['receipt_time_out']
                pr.endTime = pro['end_time']
                pr.delayedCount = pro['delayed_count']
                order = OrderModel.objects(orderid=pro['order_id']).first()
                if not order:
                    await self.getOrders(oid=pro['order_id'], limit=1)
                    order = OrderModel.objects(orderid=pro['order_id']).first()
                pr.order = order
                product = ProductModel.objects(productId=pro['pid']).first()
                if not product:
                    await self.getProducts(pid=pro['pid'], limit=1)
                    product = ProductModel.objects(productId=pro['pid']).first()
                pr.product = product
                pr.save()
                id = pr.order.orderid
            if result['more'] and id == oid:
                id += 1
            return id, result['more']
        return id, False

    async def getArbitrations(self, aid=0, limit=50):
        data = {"code": self.config['contract'], "scope": self.config['contract'], "table": "arbitrations", "lower_bound": aid, "limit": limit, "json": True}
        result = await self._post(json=data)
        id = aid
        if result and len(result['rows']) > 0:
            for arb in result['rows']:
                a = ArbitrationModel(aid=arb['id'])
                a.type = arb['type']
                a.status = arb['status']
                a.title = arb['title']
                a.resume = arb['resume']
                a.detailed = arb['detailed']
                a.createTime = arb['create_time']
                a.proofContent = arb['proof_content']
                a.arbitrationResults = arb['arbitration_results']
                a.startTime = arb['start_time']
                a.endTime = arb['end_time']
                a.reviewers = arb['reviewers']
                plaintiff = UserModel.objects(userid=arb['plaintiff']).first()
                if not plaintiff:
                    await self.getUsers(userid=arb['plaintiff'], limit=1)
                    plaintiff = UserModel.objects(userid=arb['plaintiff']).first()
                a.plaintiff = plaintiff
                product = ProductModel.objects(pid=arb['pid']).first()
                if not product:
                    await self.getProducts(pid=arb['pid'], limit=1)
                    product = ProductModel.objects(pid=arb['pid']).first()
                a.product = product
                order = None
                if len(arb['order_id']) > 0:
                    order = OrderModel.objects(oid=arb['order_id']).first()
                    if not order:
                        await self.getOrders(oid=arb['order_id'], limit=1)
                        order = OrderModel.objects(oid=arb['order_id']).first()
                a.order = order
                defendant = UserModel.objects(userid=arb['defendant']).first()
                if not defendant:
                    await self.getUsers(userid=arb['defendant'], limit=1)
                    defendant = UserModel.objects(userid=arb['defendant']).first()
                a.defendant = defendant
                winner = None
                if arb['winner'] > 0:
                    winner = UserModel.objects(userid=arb['winner']).first()
                    if not winner:
                        await self.getUsers(userid=arb['winner'], limit=1)
                        winner = UserModel.objects(userid=arb['winner']).first()
                a.winner = winner
                a.save()
                id = a.aid
            if result['more'] and id == aid:
                id += 1
            return id, result['more']
        return id, False

    async def getOtherAddrs(self, oaid=0, limit=50):
        data = {"code": self.config['contract'], "scope": self.config['contract'], "table": "otheraddr", "lower_bound": oaid, "limit": limit, "json": True}
        result = await self._post(json=data)
        id = oaid
        if result and len(result['rows']) > 0:
            for oad in result['rows']:
                oa = OtherAddrModel(oaid=oad['id'])
                user = UserModel.objects(userid=oad['uid']).first()
                if not user:
                    await self.getUsers(userid=oad['uid'], limit=1)
                    user = UserModel.objects(userid=oad['uid']).first()
                oa.user = user
                oa.coinType = oad['coin_type']
                oa.addr = oad['addr']
                oa.save()
                id = oa.oaid
            if result['more'] and id == oaid:
                id += 1
            return id, result['more']
        return id, False