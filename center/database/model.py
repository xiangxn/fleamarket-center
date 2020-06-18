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
    
class Tokens(me.Document):
    meta = {"collection": "tokens"}
    
    phone = me.StringField(required=True, primary_key=True)
    token = me.StringField(required=True)
    expiration = me.IntField(required=True)

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
    followTotal = me.IntField(default=0)
    favoriteTotal = me.IntField(default=0)
    fansTotal = me.IntField(default=0)
    authKey = me.StringField()
    
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
    releaseTime = me.StringField(required=True)
    desc = me.StringField()
    imgs = me.ListField()
    collections = me.IntField(default=0)
    price = me.StringField(required=True)
    saleMethod = me.IntField(default=0)
    seller = me.ReferenceField(User)
    #reviewer = me.ReferenceField(User)
    stockCount = me.IntField(default=0)
    isRetail = me.BooleanField(default=False)
    
class Auction(me.Document):
    meta = {"collection": "auction"}
    
    aid = me.IntField(required=True, primary_key=True)
    security = me.StringField(required=True)
    markup = me.StringField(required=True)
    currentPrice = me.StringField()
    auctionTimes = me.IntField(default=0)
    startTime = me.StringField(required=True)
    endTime = me.StringField(required=True)
    lastPriceUser = me.ReferenceField(User)
    product = me.ReferenceField(Product)
    
class Reviewer(me.Document):
    meta = {"collection": "reviewer"}
    
    rid = me.IntField(required=True, primary_key=True)
    user = me.ReferenceField(User)
    #userid = me.IntField(required=True)
    eosid = me.StringField(required=True)
    votedCount = me.IntField(default=0)
    createTime = me.StringField()
    lastActiveTime = me.StringField()
    voterApprove = me.ListField()
    voterAgainst = me.ListField()
    
    
class ProductAudit(me.Document):
    meta = {"collection": "product_audit"}
    
    paid = me.IntField(required=True, primary_key=True)
    product = me.ReferenceField(Product)
    #productId = me.IntField(required=True)
    reviewer = me.ReferenceField(Reviewer)
    isDelisted = me.IntField(default=0)
    reviewDetails = me.StringField()
    reviewTime = me.StringField()
    
class Order(me.Document):
    meta = {"collection": "order"}
    
    orderid = me.StringField(required=True, primary_key=True)
    productInfo = me.ReferenceField(Product, required=True)
    seller = me.ReferenceField(User, required=True)
    buyer = me.ReferenceField(User)
    status = me.IntField(default=0)
    price = me.StringField(required=True)
    postage = me.StringField()
    payAddr = me.StringField()
    shipNum = me.StringField()
    createTime = me.StringField(required=True)
    payTime = me.StringField()
    payOutTime = me.StringField()
    shipTime = me.StringField()
    shipOutTime = me.StringField()
    receiptTime = me.StringField()
    receiptOutTime = me.StringField()
    endTime = me.StringField()
    delayedCount = me.IntField()
    
class ProReturn(me.Document):
    meta = {"collection": "proreturn"}
    
    prid = me.IntField(required=True, primary_key=True)
    #orderId = me.StringField(required=True)
    order = me.ReferenceField(Order)
    #prodcutId = me.IntField()
    product = me.ReferenceField(Product)
    orderPrice = me.StringField()
    status = me.IntField(default=0)
    reasons = me.StringField()
    createTime = me.StringField(required=True)
    shipNum = me.StringField()
    shipTime = me.StringField()
    shipOutTime = me.StringField()
    receiptTime = me.StringField()
    receiptOutTime = me.StringField()
    endTime = me.StringField()
    delayedCount = me.IntField(default=0)
    
class Arbitration(me.Document):
    meta = {"collection": "arbitrations"}
    
    aid = me.IntField(required=True, primary_key=True)
    plaintiff = me.ReferenceField(User, required=True)
    product = me.ReferenceField(Product)
    order = me.ReferenceField(Order)
    type = me.IntField(default=0)
    status = me.IntField(default=0)
    title = me.StringField()
    resume = me.StringField()
    detailed = me.StringField()
    createTime = me.StringField()
    defendant = me.ReferenceField(User, required=True)
    proofContent = me.StringField()
    arbitrationResults = me.StringField()
    winner = me.ReferenceField(User)
    startTime = me.StringField()
    endTime = me.StringField()
    reviewers = me.ListField()
    
class OtherAddr(me.Document):
    meta = {"collection": "otheraddr"}
    
    oaid = me.IntField(required=True, primary_key=True)
    user = me.ReferenceField(User, required=True)
    coinType = me.StringField(required=True)
    addr = me.StringField(required=True)
    
class Follow(me.Document):
    meta = {"collection": "follows"}
    
    fid = me.SequenceField(primary_key=True)
    user = me.ReferenceField(User)
    follower = me.ReferenceField(User)
    
class Favorite(me.Document):
    meta = {"collection": "favorites"}
    
    cid = me.SequenceField(primary_key=True)
    user = me.ReferenceField(User)
    product = me.ReferenceField(Product)
    
class ReceiptAddress(me.Document):
    meta = {"collection": "receiptaddrs"}
    
    rid = me.SequenceField(primary_key=True)
    userid = me.IntField(required=True)
    province = me.StringField(required=True)
    city = me.StringField(required=True)
    district = me.StringField(required=True)
    phone = me.StringField(required=True)
    name = me.StringField(required=True)
    address = me.StringField(required=True)
    postcode = me.StringField(required=True)
    default = me.IntField(default=0)
    
    
    
    