import graphene
import mongoengine
from mongoengine.queryset.visitor import Q
from graphene_mongo import MongoengineObjectType, MongoengineConnectionField
from .model import User as UserModel
from .model import Category as CategoryModel
from .model import Reviewer as ReviewerModel
from .model import Product as ProductModel
#import json

#mongoengine.connect(db="bf_center", host="localhost", port=3001)
class User(MongoengineObjectType):
    class Meta:
        model = UserModel
        interfaces = (graphene.relay.Node,)
        
class Category(MongoengineObjectType):
    class Meta:
        model = CategoryModel
        interfaces = (graphene.relay.Node,)
        
class Reviewer(MongoengineObjectType):
    class Meta:
        model = ReviewerModel
        interfaces = (graphene.relay.Node,)
        
class Product(MongoengineObjectType):
    class Meta:
        model = ProductModel
        interfaces = (graphene.relay.Node,)
        
class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    # User
    user = graphene.Field(User, userid=graphene.Int())
    users = MongoengineConnectionField(User)
    user_page = graphene.List(User, pageNo=graphene.Int(default_value=1), pageSize=graphene.Int(default_value=10))
    
    #Category
    categories = MongoengineConnectionField(Category)
    
    #Reviewer
    reviewers = MongoengineConnectionField(Reviewer)
    
    #Product
    product_by_cid = graphene.List(Product, categoryId=graphene.Int(default_value=1), userid=graphene.Int(default_value=0),
                                   pageNo=graphene.Int(default_value=1), pageSize=graphene.Int(default_value=10))
    
    
    def resolve_user(self, info, userid):
        return UserModel.objects.get(userid=userid)
    
    def resolve_user_page(self, info, pageNo, pageSize):
        offset = (pageNo-1)*pageSize
        return list(UserModel.objects.skip(offset).limit(pageSize))
    
    def resolve_product_by_cid(self, info, categoryId, userid, pageNo, pageSize):
        offset = (pageNo-1)*pageSize
        if userid == 0:
            return list(ProductModel.objects(category__cid=categoryId).skip(offset).limit(pageSize))
        else:
            return list(ProductModel.objects(Q(category__cid=categoryId) & Q(seller__userid=userid)).skip(offset).limit(pageSize))
        
    
    
schema = graphene.Schema(query=Query, types=[User])
# query = '''
# {
#     users (status:0) {
#         edges {
#             node {
#                 userid,
#                 eosid
#             }
#         }
#     }
# }
# '''.strip()
# query2 = '''
# {
#     user (userid:2) {
#         userid,
#         eosid,
#         status,
#         nickname
#     }
# }
# '''
# result = schema.execute(query)
# print(json.dumps(result.data))
