import sys
sys.path.append('../center')
import pytest
from center.eoslib.keys import PrivateKey, PublicKey
from center.eoslib.memo import encode_memo, decode_memo
from center.eoslib.signature import sign_message, verify_message
from binascii import hexlify, unhexlify
from center.utils import Utils
import random
import json

parametrize = pytest.mark.parametrize

class TestKey(object):
    
    def test_keys(self):
        priKey = PrivateKey("5JTjhoW4cbBDcHkfDVE6C3DwHqgU4yccqTAxrV7xc7JMDwa1xja")
        assert str(priKey.pubkey) == "EOS5BiYrPwXwFmrjLQ3ZUa3BX9crdomJNfYdu6uC863XAXrHNyWbo"
        
        pubKey = PublicKey("EOS5BiYrPwXwFmrjLQ3ZUa3BX9crdomJNfYdu6uC863XAXrHNyWbo")
        assert str(pubKey)== "EOS5BiYrPwXwFmrjLQ3ZUa3BX9crdomJNfYdu6uC863XAXrHNyWbo"
        
    def test_memo(self):
        nonce = "".join(random.sample('0123456789',8))
        print("nonce={}".format(nonce))
        priKey = PrivateKey("5JTjhoW4cbBDcHkfDVE6C3DwHqgU4yccqTAxrV7xc7JMDwa1xja")
        pubKey = PublicKey("EOS6RbTLtFQ49MKa8epucQT7FvTjcCHgLc58FzY9mcPVcN94omxtT")
        msg = "18580555555"
        en_msg = encode_memo(priKey, pubKey, nonce, msg)
        print("en_msg={}".format(en_msg))
        priKey = PrivateKey("5JEqeNHksYz3Q47rKjPfMvP1D64X2JA61Qp9kMdLmaT7vKGiXZL")
        pubKey = PublicKey("EOS5BiYrPwXwFmrjLQ3ZUa3BX9crdomJNfYdu6uC863XAXrHNyWbo")
        de_msg = decode_memo(priKey, pubKey, nonce, en_msg)
        assert de_msg == msg
        
    def test_sign(self):
        priKey = PrivateKey("5JTjhoW4cbBDcHkfDVE6C3DwHqgU4yccqTAxrV7xc7JMDwa1xja")
        source_msg = "1399809098200"
        sign_msg = sign_message(source_msg, priKey)
        print("sign_msg: ", sign_msg)
        #shex = hexlify(sign_msg).decode("ascii")
        #print("sign_msg: ", shex)
        p = verify_message(source_msg, sign_msg)
        phex = hexlify(p).decode("latin")
        #print("phex: ",phex, repr(priKey.pubkey))
        pubKey = PublicKey(phex)
        print("pubkey: ", pubKey, priKey.pubkey)
        assert str(priKey.pubkey) == str(pubKey)
        
    def test_hash(self):
        data={"id":1}
        m= json.dumps(data)
        print("m:{}".format(m))
        print(m.encode())
        hash = Utils.sha256(m.encode())
        print('hash:{}'.format(hash))