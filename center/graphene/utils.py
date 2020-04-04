import sys

def _bytes(x):  # pragma: no branch
    """ Python3 and Python2 compatibility
    """
    if sys.version > "3":
        return bytes(x, "utf8")
    else:  # pragma: no cover
        return x.__bytes__()