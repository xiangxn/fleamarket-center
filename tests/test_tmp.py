import sys
sys.path.append('../center')
import pytest
import time

parametrize = pytest.mark.parametrize


class TestKey(object):
    def test_orderid(self):
        userid = 123
        pid = 456
        t = 1603459511  # int(time.time())
        print("t:{}".format(t))
        orderid = ((userid << 64) | (pid << 32)) | t
        print("orderid: {}".format(orderid))
        print("userid: {}".format(orderid >> 64))
        print("pid: {}".format(((orderid << 64) >> 64) >> 32))

        x = 18446744083902945719
        print(str(x))
        x = x << 64
        print("x1: {}".format(x))
        x = x >> 64
        print("x11: {}".format(x))
        x = x << 32
        print("x2: {}".format(x))
        x = x >> 64
        print("x3: {}".format(x))
        print(str(x))
