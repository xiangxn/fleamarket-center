import hashlib
import random

from center.eoslib.keys import PrivateKey, PublicKey
from center.eoslib.memo import encode_memo, decode_memo

class Utils:
    
    @classmethod
    def sha256(cls, data):
        return hashlib.sha256(data).hexdigest()
    
    @classmethod
    def char_to_value(cls, c):
        oc = ord(c)
        if oc >= ord('a') and oc <= ord('z'):
            return (oc - ord('a')) + 6
        if oc >= ord('1') and oc <= ord('5'):
            return (oc - ord('1')) + 1
        return 0
    
    @classmethod
    def string_to_uint64(cls, strs):
        n = 0
        l = len(strs)
        cs = strs if l <= 12 else strs[0:12] 
        for c in cs:
            n <<= 5
            n |= cls.char_to_value(c)
        n <<= ( 4 + 5*(12 - l) )
        if l > 12:
            n |= cls.char_to_value(strs[12]) & int(0x0F)
        return n
    
    @staticmethod
    def encrypt_phone(phone, active, sKey):
        nonce = "".join(random.sample('0123456789',8))
        priKey = PrivateKey(sKey)
        pubKey = PublicKey(active)
        en_msg = encode_memo(priKey, pubKey, nonce, phone)
        return nonce+en_msg
    
    @staticmethod
    def decrypt_phone(phone_encrypt, active, sKey):
        nonce = phone_encrypt[0:8]
        en_msg = phone_encrypt[8:]
        priKey = PrivateKey(sKey)
        pubKey = PublicKey(active)
        return decode_memo(priKey, pubKey, nonce, en_msg)

