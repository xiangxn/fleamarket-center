import graphene
import mongoengine
from mongoengine.queryset.visitor import Q
from graphene_mongo import MongoengineObjectType, MongoengineConnectionField
from .model import User as UserModel
from .model import Category as CategoryModel
from .model import Reviewer as ReviewerModel
from .model import Product as ProductModel
from .model import Order as OrderModel
from .model import ProductAudit as ProductAuditModel
from .model import OtherAddr as OtherAddrModel
from .model import Follow as FollowModel
from .model import Collect as CollectModel
#import json

#mongoengine.connect(db="bf_center", host="localhost", port=3001)
class User(MongoengineObjectType):
    class Meta:
        model = UserModel
        interfaces = (graphene.relay.Node,)
        
class OtherAddr(MongoengineObjectType):
    class Meta:
        model = OtherAddrModel
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
        
class ProductAudit(MongoengineObjectType):
    class Meta:
        model = ProductAuditModel
        interfaces = (graphene.relay.Node,)
        
class Order(MongoengineObjectType):
    class Meta:
        model = OrderModel
        interfaces = (graphene.relay.Node,)
        
class Follow(MongoengineObjectType):
    class Meta:
        model = FollowModel
        interfaces = (graphene.relay.Node,)
        
class Collect(MongoengineObjectType):
    class Meta:
        model = CollectModel
        interfaces = (graphene.relay.Node,)
        
class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    # User
    user = graphene.Field(User, userid=graphene.Int())
    users = MongoengineConnectionField(User)
    user_page = graphene.List(User, pageNo=graphene.Int(default_value=1), pageSize=graphene.Int(default_value=10))
    
    # OtherAddr
    withdraw_addr = graphene.List(OtherAddr, userid=graphene.Int(default_value=0))
    
    #Category
    categories = MongoengineConnectionField(Category)
    
    #Reviewer
    reviewers = MongoengineConnectionField(Reviewer)
    
    #Product
    product_by_cid = graphene.List(Product, categoryId=graphene.Int(default_value=1), userid=graphene.Int(default_value=0),
                                   pageNo=graphene.Int(default_value=1), pageSize=graphene.Int(default_value=10))
    product_by_publisher = graphene.List(Product, userid=graphene.Int(default_value=1),
                                         pageNo=graphene.Int(default_value=1), pageSize=graphene.Int(default_value=10))
    product_audits = MongoengineConnectionField(ProductAudit)
    products = MongoengineConnectionField(Product)
    
    #Order
    order_by_buyer = graphene.List(Order, userid=graphene.Int(default_value=0),
                                   pageNo=graphene.Int(default_value=1), pageSize=graphene.Int(default_value=10))
    order_by_seller = graphene.List(Order, userid=graphene.Int(default_value=0),
                                   pageNo=graphene.Int(default_value=1), pageSize=graphene.Int(default_value=10))
    order_by_id = graphene.List(Order, orderid=graphene.String())
    
    #Follow
    follows = MongoengineConnectionField(Follow)
    follow_by_user = graphene.List(Follow, userid=graphene.Int(default_value=0),
                                   pageNo=graphene.Int(default_value=1), pageSize=graphene.Int(default_value=10))
    follow_by_follower = graphene.List(Follow, userid=graphene.Int(default_value=0),
                                   pageNo=graphene.Int(default_value=1), pageSize=graphene.Int(default_value=10))
    
    #Collect
    collects = MongoengineConnectionField(Collect)
    collect_by_user = graphene.List(Collect, userid=graphene.Int(default_value=0),
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
        
    def resolve_product_by_publisher(self, info, userid, pageNo, pageSize):
        offset = (pageNo-1)*pageSize
        return list(ProductModel.objects(seller__userid=userid).skip(offset).limit(pageSize))
    
    def resolve_order_by_buyer(self, info, userid, pageNo, pageSize):
        offset = (pageNo-1)*pageSize
        return list(OrderModel.objects(buyer__userid=userid).skip(offset).limit(pageSize))
    
    def resolve_order_by_seller(self, info, userid, pageNo, pageSize):
        offset = (pageNo-1)*pageSize
        return list(OrderModel.objects(seller__userid=userid).skip(offset).limit(pageSize))
    
    def resolve_order_by_id(self, info, orderid):
        return OrderModel.objects(orderid=orderid).first()
    
    def resolve_withdraw_addr(self, info, userid):
        return list(OtherAddrModel.objects(user__userid=userid))
        
    
    
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
