import asyncio
import aiohttp
import mongoengine
import json

from mongoengine.queryset.visitor import Q

from center.gateway import Gateway
from center.logger import Logger
from center.database.model import TableLog as TableLogModel
from center.database.model import User as UserModel
from center.database.model import Category as CategoryModel


class SyncSvr:
    
    def __init__(self, config, get_init=False):
        self.logger = Logger("sync")
        self.config = config['sync_cfg']
        self.db_config = config['mongo']
        self.get_init = get_init
        self._init_db()
        self.gateway = Gateway(config['gateway'], self.logger)
        
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
        trx = {"transaction":{"actions": [payload]}}
        result = self.gateway.broadcast(trx, sign=True)
        if result['status'] == "success":
            print("The chain log of [{}] has been deleted".format(tid))
        else:
            self.logger.Error("Failed to delete logs on the chain", None, result, screen=True)
        
    async def _post(self, data=None, json=None, uri="get_table_rows"):
        result = None
        url = self.config['api_url']
        url = "{}{}{}".format(url, ("" if url.endswith("/") else "/"), uri)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, data=data, json=json) as response:
                    if response.status == 200 or response.status == 202:
                        result = await response.json()
            except Exception as e:
                print("post error: ", e)
        return result
    
    def getIncrementTasks(self, loop):
        tasks = [loop.create_task(self.taskSyncTableLog()),
                    loop.create_task(self.taskSyncUser())]
        return tasks
    
    def getInitTasks(self, loop):
        tasks = []
        # users
        async def syncUser(userid=0, limit=50):
            try:
                uid, more = await self.getUsers(userid, limit)
                while(more):
                    uid, more = await self.getUsers(uid, limit)
                print("Sync to userid:{}".format(uid))
            except KeyboardInterrupt as ke:
                print("init users sync stop...")
        tasks.append(loop.create_task(syncUser()))
        
        #Categories
        async def syncCategory(cid=0, limit=50):
            try:
                id, more = await self.getCategorys(cid, limit=limit)
                while(more):
                    id, more = await self.getCategorys(id, limit=limit)
                print("Sync to cid:{}".format(id))
            except KeyboardInterrupt as ke:
                print("init categories sync stop...")
        tasks.append(loop.create_task(syncCategory()))
                
        
        
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
        
    async def taskSyncTableLog(self):
        try:
            while(True):
                tid, more = await self.getTableLogs(0)
                while(more):
                    tid, more = await self.getTableLogs(tid)
                    await asyncio.sleep(2)
                if tid > 0:
                    self._deleteLogs(tid)
                await asyncio.sleep(self.config['sync_log_interval'])
        except KeyboardInterrupt as ke:
            print("Table log sync stop...")
        
    async def taskSyncUser(self):
        try:
            while(True):
                logs = TableLogModel.objects(table="users").limit(50)
                uid=0
                more=False
                for log in logs:
                    uid, more = await self.getUsers(userid=int(log.primary), limit=1)
                    log.delete()
                #print("Sync to userid:{}".format(uid))
                await asyncio.sleep(5)
        except KeyboardInterrupt as ke:
            print("users sync stop...")
        
    
    async def getTableLogs(self, id=0, limit=50):
        data = {
            "code": self.config['contract'],
            "scope": self.config['contract'],
            "table":"tablelogs",
            "lower_bound": id,
            "limit": limit,
            "json": True
        }
        tid = id
        result = await self._post(json=data)
        if result and len(result['rows']) > 0:
            for log in result['rows']:
                ol = TableLogModel.objects(Q(table=log['table']) & Q(primary=log['primary'])).first()
                if ol is None:
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
                u.phone = user['phone_encrypt']
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
                u.isReviewer = user['is_reviewer']
                u.save()
                uid = u.userid
            return uid, result['more']
        return uid, False
    
    async def getCategorys(self, cid=0, limit=50):
        data = {
            "code": self.config['contract'],
            "scope": self.config['contract'],
            "table": "categories",
            "lower_bound": cid,
            "limit": limit,
            "json": True
        }
        result = await self._post(json=data)
        if result and len(result['rows']) > 0:
            for cate in result['rows']:
                c = CategoryModel(cid=cate['id'])
                c.view = cate['view']
                c.parent = cate['parent']
                c.save()
                id = c.cid
            return id, result['more']
        return cid, False