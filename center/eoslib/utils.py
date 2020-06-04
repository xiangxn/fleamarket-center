import sys
import hashlib

def _bytes(x):  # pragma: no branch
    """ Python3 and Python2 compatibility
    """
    if sys.version > "3":
        return bytes(x, "utf8")
    else:  # pragma: no cover
        return x.__bytes__()
    
def sha256(data):
    ''' '''
    return hashlib.sha256(data).hexdigest()

def ripemd160(data):
    ''' '''
    #h = hashlib.new('ripemd160')
    h = hashlib.new('rmd160')
    h.update(data)
    return h.hexdigest()