import mongoengine as me

class TableLog(me.Document):
    meta = {"collection": "tablelog"}
    
    tid = me.IntField(required=True, primary_key=True)
    table = me.StringField(required=True)
    ttype = me.IntField(required=True)
    primary = me.StringField(required=True)
    
class Sms(me.Document):
    meta = {"collection": "sms"}
    
    phone = me.StringField(required=True, primary_key=True)
    code = me.StringField(required=True)
    time = me.IntField(required=True)

class User(me.Document):
    meta = {"collection": "user"}
    
    userid = me.IntField(required=True, primary_key=True)
    eosid = me.StringField(required=True)
    phone = me.StringField(required=True)
    status = me.IntField(required=True)
    nickname = me.StringField(required=True)
    head = me.StringField(required=True)
    creditValue = me.IntField(required=True)
    referrer = me.StringField(required=True)
    lastActiveTime = me.StringField()
    postsTotal = me.IntField()
    sellTotal = me.IntField()
    buyTotal = me.IntField()
    referralTotal = me.IntField()
    point = me.StringField()
    isReviewer = me.IntField()
    favoriteTotal = me.IntField(default=0)
    collectionTotal = me.IntField(default=0)
    fansTotal = me.IntField(default=0)
    
    def __str__(self):
        return self.to_json()
    
class Category(me.Document):
    meta = {"collection": "category"}
    
    cid = me.IntField(required=True, primary_key=True)
    view = me.StringField(required=True)
    parent = me.IntField(required=True)
    
class Product(me.Document):
    meta = {"collection": "product"}
    
    productId = me.IntField(required=True, primary_key=True)
    #categoryId = me.IntField(required=True)
    category = me.ReferenceField(Category, required=True)
    title = me.StringField(required=True)
    status = me.IntField(required=True)
    isNew = me.IntField(default=0)
    isReturns = me.IntField(default=0)
    transMethod = me.IntField(default=1)
    postage = me.StringField()
    position = me.StringField()
    releaseTime = me.DateTimeField(required=True)
    desc = me.StringField()
    imgs = me.ListField()
    collections = me.IntField(default=0)
    price = me.StringField(required=True)
    saleMethod = me.IntField(default=0)
    seller = me.ReferenceField(User)
    reviewer = me.ReferenceField(User)
    stockCount = me.IntField(default=0)
    isRetail = me.BooleanField(default=False)
    
class Auction(me.Document):
    meta = {"collection": "auction"}
    
    aid = me.IntField(required=True, primary_key=True)
    security = me.StringField(required=True)
    markup = me.StringField(required=True)
    currentPrice = me.StringField()
    auctionTimes = me.IntField(default=0)
    startTime = me.DateTimeField(required=True)
    endTime = me.DateTimeField(required=True)
    lastPriceUser = me.ReferenceField(User)
    product = me.ReferenceField(Product)
    
class Reviewer(me.Document):
    meta = {"collection": "reviewer"}
    
    rid = me.IntField(required=True, primary_key=True)
    user = me.ReferenceField(User)
    userid = me.IntField(required=True)
    eosid = me.StringField(required=True)
    votedCount = me.IntField(default=0)
    createTime = me.DateTimeField()
    lastActiveTime = me.DateTimeField()
    voterApprove = me.ListField()
    voterAgainst = me.ListField()
    
    
class ProductAudit(me.Document):
    meta = {"collection": "product_audit"}
    
    paid = me.IntField(required=True, primary_key=True)
    product = me.ReferenceField(Product)
    productId = me.IntField(required=True)
    reviewer = me.ReferenceField(Reviewer)
    isDelisted = me.IntField(default=0)
    reviewDetails = me.StringField()
    reviewTime = me.DateTimeField()
    
class Order(me.Document):
    meta = {"collection": "order"}
    
    orderid = me.StringField(required=True, primary_key=True)
    prodcutInfo = me.ReferenceField(Product, required=True)
    seller = me.ReferenceField(User, required=True)
    buyer = me.ReferenceField(User)
    status = me.IntField(default=0)
    price = me.StringField(required=True)
    shipNum = me.StringField()
    createTime = me.DateTimeField(required=True)
    payTime = me.DateTimeField()
    payOutTime = me.DateTimeField()
    shipTime = me.DateTimeField()
    shipOutTime = me.DateTimeField()
    receiptTime = me.DateTimeField()
    receiptOutTime = me.DateTimeField()
    
class ProReturn(me.Document):
    meta = {"collection": "proreturn"}
    
    rpid = me.IntField(required=True, primary_key=True)
    order = me.ReferenceField(Order)
    orderId = me.StringField(required=True)
    prodcutId = me.IntField()
    orderPrice = me.StringField()
    status = me.IntField(default=0)
    reasons = me.StringField()
    createTime = me.DateTimeField(required=True)
    shipNum = me.StringField()
    shipTime = me.DateTimeField()
    shipOutTime = me.DateTimeField()
    receiptTime = me.DateTimeField()
    receiptOutTime = me.DateTimeField()
    endTime = me.DateTimeField()
    delayedCount = me.IntField(default=0)
    
    
    