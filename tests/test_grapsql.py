import sys
sys.path.append('../center')
import pytest
import time
from eospy.utils import decimalToBinary

import json
import mongoengine
import graphene
from graphene_mongo import MongoengineObjectType, MongoengineConnectionField
from center.database.schema import ProReturn

parametrize = pytest.mark.parametrize


class TestGrapSQL(object):
    def test_filter_by_reference(self):
        class Query(graphene.ObjectType):
            returns = MongoengineConnectionField(ProReturn)

        query = '''
        {returns(order:1){edges{node{prid}}}}
        '''
        mongoengine.connect(db="bf_center", host="localhost", port=3001)

        schema = graphene.Schema(query=Query)
        result = schema.execute(query)
        print(json.dumps(result.data))
