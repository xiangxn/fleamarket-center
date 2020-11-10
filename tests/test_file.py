import sys
sys.path.append('../center')
import pytest

import grpc
from center.rpc.bitsflea_pb2 import FileRequest
from center.rpc.bitsflea_pb2_grpc import BitsFleaStub


parametrize = pytest.mark.parametrize

class AuthGateway(grpc.AuthMetadataPlugin):
    
    def __call__(self, context, callback):
        callback((("token", "2d1fa81d93c7201ed171a67738de27182abb6e6e0eb3b621f7af0c82d2882d0c"),), None)
        
class TestFile(object):
    
    def test_file(self):
        file = "/Users/necklace/work/FM/fleamarket-center/logo.png"
        # fp = open(file, "rb")
        # content = fp.read()
        # print(content.hex())
        # fp.close()
        # call_cred = grpc.metadata_call_credentials(AuthGateway(), name="auth gateway")
        # creds = grpc.composite_call_credentials(call_cred)
        # grpc.ClientCallDetails
        # with grpc.insecure_channel("127.0.0.1:50000") as channel:
        #     client = BitsFleaStub(channel)
        #     data = (('token','64ca0872ba482773a95791cc011baf76d6f3c32b55d995e6467826055ae89bfa'),)
        #     res = client.Upload(FileRequest(file=content,name="logo.jpg"), metadata=data)
        #     print(res)
        