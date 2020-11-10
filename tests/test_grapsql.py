import sys
sys.path.append('../center')
import pytest
import time
from eospy.utils import decimalToBinary

import json
import mongoengine
import graphene
from graphene_mongo import MongoengineObjectType, MongoengineConnectionField
from center.database.schema import ProReturn, OrderModel

parametrize = pytest.mark.parametrize


class TestGrapSQL(object):
    # def test_graphene_mongo(self):
    #     mongoengine.connect(db="bf_center", host="localhost", port=3001)
    #     data = OrderModel.objects(buyer=1).order_by("-createTime").skip(0).limit(20)
    #     print("data: {} {}".format(data.to_json(),data[0].id))
        
    # def test_query(self):
    #     from center.database.schema import Query
    #     mongoengine.connect(db="bf_center", host="localhost", port=3001)
    #     query = '''
    #     {orderByBuyer(userid:1,pageNo:1,pageSize:20){pageNo,pageSize,totalCount,list{oid,orderid,buyer{userid,nickname,head}}}}
    #     '''
    #     schema = graphene.Schema(query=Query)
    #     result = schema.execute(query)
    #     print(json.dumps(result.data))

    def test_filter_by_reference(self):
        from center.database.schema import Query

        query = '''
        {returnsByOrder(order:1){prid,order{orderid}}}
        '''
        mongoengine.connect(db="bf_center", host="localhost", port=3001)

        schema = graphene.Schema(query=Query)
        result = schema.execute(query)
        print(json.dumps(result.data))
