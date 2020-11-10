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
from .model import Favorite as FavoriteModel
from .model import ReceiptAddress as ReceiptAddressModel
from .model import ProReturn as ProReturnModel
from collections import OrderedDict

#import json


#mongoengine.connect(db="bf_center", host="localhost", port=3001)
class PageConnection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        print(info)
        print(kwargs)
        return root.list_length


class User(MongoengineObjectType):
    class Meta:
        model = UserModel
        interfaces = (graphene.relay.Node, )


class OtherAddr(MongoengineObjectType):
    class Meta:
        model = OtherAddrModel
        interfaces = (graphene.relay.Node, )


class Category(MongoengineObjectType):
    class Meta:
        model = CategoryModel
        interfaces = (graphene.relay.Node, )
        connection_class = PageConnection


class Reviewer(MongoengineObjectType):
    class Meta:
        model = ReviewerModel
        interfaces = (graphene.relay.Node, )


class Product(MongoengineObjectType):
    class Meta:
        model = ProductModel
        interfaces = (graphene.relay.Node, )


class ProductAudit(MongoengineObjectType):
    class Meta:
        model = ProductAuditModel
        interfaces = (graphene.relay.Node, )


class Order(MongoengineObjectType):
    class Meta:
        model = OrderModel
        interfaces = (graphene.relay.Node, )


class Follow(MongoengineObjectType):
    class Meta:
        model = FollowModel
        interfaces = (graphene.relay.Node, )


class Favorite(MongoengineObjectType):
    class Meta:
        model = FavoriteModel
        interfaces = (graphene.relay.Node, )


class ReceiptAddress(MongoengineObjectType):
    class Meta:
        model = ReceiptAddressModel
        interfaces = (graphene.relay.Node, )


class ProReturn(MongoengineObjectType):
    class Meta:
        model = ProReturnModel
        interfaces = (graphene.relay.Node, )


def _create_page_type(obj_type):
    return type("Page{}".format(obj_type), (graphene.ObjectType, ), {
        'pageNo': graphene.Int(),
        'pageSize': graphene.Int(),
        'totalCount': graphene.Int(),
        'list': graphene.List(obj_type)
    })


PageUser = _create_page_type(User)
PageProduct = _create_page_type(Product)
PageOrder = _create_page_type(Order)
PageFollow = _create_page_type(Follow)
PageFavorite = _create_page_type(Favorite)
PageReviewer = _create_page_type(Reviewer)
PageProReturn = _create_page_type(ProReturn)


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    # User
    user = graphene.Field(User, userid=graphene.Int())
    users = MongoengineConnectionField(User)
    user_page = graphene.Field(PageUser, pageNo=graphene.Int(default_value=1), pageSize=graphene.Int(default_value=10))
    user_invited = graphene.Field(PageUser, ref=graphene.String(), pageNo=graphene.Int(default_value=1), pageSize=graphene.Int(default_value=10))

    # OtherAddr
    withdraw_addr = graphene.List(OtherAddr, userid=graphene.Int(default_value=0))

    #Category
    categories = MongoengineConnectionField(Category)

    #Reviewer
    reviewers = MongoengineConnectionField(Reviewer)
    reviewer_page = graphene.Field(PageReviewer, pageNo=graphene.Int(default_value=1), pageSize=graphene.Int(default_value=10))

    #Product
    product_by_cid = graphene.Field(PageProduct,
                                    categoryId=graphene.Int(default_value=1),
                                    userid=graphene.Int(default_value=0),
                                    pageNo=graphene.Int(default_value=1),
                                    pageSize=graphene.Int(default_value=10))

    product_by_title = graphene.Field(PageProduct,
                                      title=graphene.String(),
                                      userid=graphene.Int(default_value=0),
                                      pageNo=graphene.Int(default_value=1),
                                      pageSize=graphene.Int(default_value=10))

    product_by_publisher = graphene.Field(PageProduct,
                                          userid=graphene.Int(default_value=1),
                                          pageNo=graphene.Int(default_value=1),
                                          pageSize=graphene.Int(default_value=10))
    product_by_status = graphene.Field(PageProduct,
                                       status=graphene.Int(default_value=1),
                                       ignoreUid=graphene.Int(default_value=0),
                                       pageNo=graphene.Int(default_value=1),
                                       pageSize=graphene.Int(default_value=10))
    product_audits = MongoengineConnectionField(ProductAudit)
    products = MongoengineConnectionField(Product)

    #Order
    order_by_buyer = graphene.Field(PageOrder,
                                    userid=graphene.Int(default_value=0),
                                    pageNo=graphene.Int(default_value=1),
                                    pageSize=graphene.Int(default_value=10))
    order_by_seller = graphene.Field(PageOrder,
                                     userid=graphene.Int(default_value=0),
                                     pageNo=graphene.Int(default_value=1),
                                     pageSize=graphene.Int(default_value=10))
    order_by_id = graphene.Field(Order, orderid=graphene.String())

    #Follow
    follows = MongoengineConnectionField(Follow)
    follow_by_user = graphene.Field(PageFollow,
                                    userid=graphene.Int(default_value=0),
                                    pageNo=graphene.Int(default_value=1),
                                    pageSize=graphene.Int(default_value=10))
    follow_by_follower = graphene.Field(PageFollow,
                                        userid=graphene.Int(default_value=0),
                                        pageNo=graphene.Int(default_value=1),
                                        pageSize=graphene.Int(default_value=10))

    #Favorite
    favorites = MongoengineConnectionField(Favorite)
    favorite_by_user = graphene.Field(PageFavorite,
                                      userid=graphene.Int(default_value=0),
                                      pageNo=graphene.Int(default_value=1),
                                      pageSize=graphene.Int(default_value=10))

    #ReceiptAddress
    receiptaddresses = MongoengineConnectionField(ReceiptAddress)
    rec_addr_by_user = graphene.List(ReceiptAddress, userid=graphene.Int(default_value=0))

    #returns
    returns_by_order = graphene.Field(ProReturn, order=graphene.Int(default_value=0) )

    def resolve_user(self, info, userid):
        return UserModel.objects.get(userid=userid)

    def resolve_user_page(self, info, pageNo, pageSize):
        offset = (pageNo - 1) * pageSize
        obj = PageUser()
        obj.pageNo = pageNo
        obj.pageSize = pageSize
        obj.totalCount = UserModel.objects().count()
        obj.list = list(UserModel.objects.skip(offset).limit(pageSize))
        return obj

    def resolve_user_invited(self, info, ref, pageNo, pageSize):
        offset = (pageNo - 1) * pageSize
        obj = PageUser()
        obj.pageNo = pageNo
        obj.pageSize = pageSize
        obj.totalCount = UserModel.objects(referrer=ref).count()
        obj.list = list(UserModel.objects(referrer=ref).order_by("-userid").skip(offset).limit(pageSize))
        return obj

    def resolve_reviewer_page(self, info, pageNo, pageSize):
        offset = (pageNo - 1) * pageSize
        obj = PageReviewer()
        obj.pageNo = pageNo
        obj.pageSize = pageSize
        obj.totalCount = ReviewerModel.objects().count()
        obj.list = list(ReviewerModel.objects.order_by("-votedCount").skip(offset).limit(pageSize))
        return obj

    def resolve_product_by_cid(self, info, categoryId, userid, pageNo, pageSize):
        offset = (pageNo - 1) * pageSize
        obj = PageProduct()
        obj.pageNo = pageNo
        obj.pageSize = pageSize
        if categoryId == 0:
            if userid == 0:
                obj.totalCount = ProductModel.objects(status=100).count()
                obj.list = list(ProductModel.objects(status=100).skip(offset).limit(pageSize))
            else:
                obj.totalCount = ProductModel.objects(Q(seller=userid) & Q(status=100)).count()
                obj.list = list(ProductModel.objects(Q(seller=userid) & Q(status=100)).skip(offset).limit(pageSize))
        else:
            if userid == 0:
                obj.totalCount = ProductModel.objects(Q(category=categoryId) & Q(status=100)).count()
                obj.list = list(ProductModel.objects(Q(category=categoryId) & Q(status=100)).skip(offset).limit(pageSize))
            else:
                obj.totalCount = ProductModel.objects(Q(category=categoryId) & Q(status=100) & Q(seller=userid)).count()
                obj.list = list(ProductModel.objects(Q(category=categoryId) & Q(status=100) & Q(seller=userid)).skip(offset).limit(pageSize))
        return obj

    def resolve_product_by_title(self, info, title, userid, pageNo, pageSize):
        offset = (pageNo - 1) * pageSize
        obj = PageProduct()
        obj.pageNo = pageNo
        obj.pageSize = pageSize
        if userid == 0:
            obj.totalCount = ProductModel.objects(title__icontains=title).count()
            obj.list = list(ProductModel.objects(title__icontains=title).skip(offset).limit(pageSize))
        else:
            obj.totalCount = ProductModel.objects(Q(title__icontains=title) & Q(seller=userid)).count()
            obj.list = list(ProductModel.objects(Q(title__icontains=title) & Q(seller=userid)).skip(offset).limit(pageSize))
        return obj

    def resolve_product_by_publisher(self, info, userid, pageNo, pageSize):
        offset = (pageNo - 1) * pageSize
        obj = PageProduct()
        obj.pageNo = pageNo
        obj.pageSize = pageSize
        obj.totalCount = ProductModel.objects(seller=userid).count()
        obj.list = list(ProductModel.objects(seller=userid).order_by("-releaseTime").skip(offset).limit(pageSize))
        return obj

    def resolve_product_by_status(self, info, status, ignoreUid, pageNo, pageSize):
        offset = (pageNo - 1) * pageSize
        obj = PageProduct()
        obj.pageNo = pageNo
        obj.pageSize = pageSize
        obj.totalCount = ProductModel.objects(Q(status=status) & Q(seller__ne=ignoreUid)).count()
        obj.list = list(ProductModel.objects(Q(status=status) & Q(seller__ne=ignoreUid)).order_by("releaseTime").skip(offset).limit(pageSize))
        return obj

    def resolve_order_by_buyer(self, info, userid, pageNo, pageSize):
        offset = (pageNo - 1) * pageSize
        obj = PageOrder()
        obj.pageNo = pageNo
        obj.pageSize = pageSize
        obj.totalCount = OrderModel.objects(buyer=userid).count()
        obj.list = list(OrderModel.objects(buyer=userid).order_by("-createTime").skip(offset).limit(pageSize))
        return obj

    def resolve_order_by_seller(self, info, userid, pageNo, pageSize):
        offset = (pageNo - 1) * pageSize
        obj = PageOrder()
        obj.pageNo = pageNo
        obj.pageSize = pageSize
        obj.totalCount = OrderModel.objects(seller=userid).count()
        obj.list = list(OrderModel.objects(seller=userid).order_by("-createTime").skip(offset).limit(pageSize))
        return obj

    def resolve_order_by_id(self, info, orderid):
        return OrderModel.objects(orderid=orderid).first()

    def resolve_follow_by_user(self, info, userid, pageNo, pageSize):
        offset = (pageNo - 1) * pageSize
        obj = PageFollow()
        obj.pageNo = pageNo
        obj.pageSize = pageSize
        obj.totalCount = FollowModel.objects(user=userid).count()
        obj.list = list(FollowModel.objects(user=userid).skip(offset).limit(pageSize))
        return obj

    def resolve_follow_by_follower(self, info, userid, pageNo, pageSize):
        offset = (pageNo - 1) * pageSize
        obj = PageFollow()
        obj.pageNo = pageNo
        obj.pageSize = pageSize
        obj.totalCount = FollowModel.objects(follower=userid).count()
        obj.list = list(FollowModel.objects(follower=userid).skip(offset).limit(pageSize))
        return obj

    def resolve_favorite_by_user(self, info, userid, pageNo, pageSize):
        offset = (pageNo - 1) * pageSize
        obj = PageFavorite()
        obj.pageNo = pageNo
        obj.pageSize = pageSize
        fms = FavoriteModel.objects(user=userid)
        obj.totalCount = fms.count()
        # pids = fms.skip(offset).limit(pageSize).scalar("product")
        # obj.list = list(ProductModel.objects(productId__in=pids))
        obj.list = list(fms.skip(offset).limit(pageSize))
        return obj

    def resolve_returns_by_order(self, info, order):
        return ProReturnModel.objects(order=order).first()

    def resolve_withdraw_addr(self, info, userid):
        return list(OtherAddrModel.objects(user=userid))

    def resolve_rec_addr_by_user(self, info, userid):
        return list(ReceiptAddressModel.objects(userid=userid))


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
