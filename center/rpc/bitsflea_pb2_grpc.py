# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import bitsflea_pb2 as bitsflea__pb2


class BitsFleaStub(object):
    """Missing associated documentation comment in .proto file"""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Register = channel.unary_unary(
                '/bitsflea.BitsFlea/Register',
                request_serializer=bitsflea__pb2.RegisterRequest.SerializeToString,
                response_deserializer=bitsflea__pb2.RegisterReply.FromString,
                )
        self.SendSmsCode = channel.unary_unary(
                '/bitsflea.BitsFlea/SendSmsCode',
                request_serializer=bitsflea__pb2.SmsRequest.SerializeToString,
                response_deserializer=bitsflea__pb2.BaseReply.FromString,
                )
        self.RefreshToken = channel.unary_unary(
                '/bitsflea.BitsFlea/RefreshToken',
                request_serializer=bitsflea__pb2.RefreshTokenRequest.SerializeToString,
                response_deserializer=bitsflea__pb2.RefreshTokenReply.FromString,
                )
        self.Referral = channel.unary_unary(
                '/bitsflea.BitsFlea/Referral',
                request_serializer=bitsflea__pb2.EosidRequest.SerializeToString,
                response_deserializer=bitsflea__pb2.BaseReply.FromString,
                )
        self.Search = channel.unary_unary(
                '/bitsflea.BitsFlea/Search',
                request_serializer=bitsflea__pb2.SearchRequest.SerializeToString,
                response_deserializer=bitsflea__pb2.SearchReply.FromString,
                )
        self.Transaction = channel.unary_unary(
                '/bitsflea.BitsFlea/Transaction',
                request_serializer=bitsflea__pb2.TransactionRequest.SerializeToString,
                response_deserializer=bitsflea__pb2.BaseReply.FromString,
                )
        self.Follow = channel.unary_unary(
                '/bitsflea.BitsFlea/Follow',
                request_serializer=bitsflea__pb2.FollowRequest.SerializeToString,
                response_deserializer=bitsflea__pb2.BaseReply.FromString,
                )


class BitsFleaServicer(object):
    """Missing associated documentation comment in .proto file"""

    def Register(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendSmsCode(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RefreshToken(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Referral(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Search(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Transaction(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Follow(self, request, context):
        """Missing associated documentation comment in .proto file"""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BitsFleaServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=bitsflea__pb2.RegisterRequest.FromString,
                    response_serializer=bitsflea__pb2.RegisterReply.SerializeToString,
            ),
            'SendSmsCode': grpc.unary_unary_rpc_method_handler(
                    servicer.SendSmsCode,
                    request_deserializer=bitsflea__pb2.SmsRequest.FromString,
                    response_serializer=bitsflea__pb2.BaseReply.SerializeToString,
            ),
            'RefreshToken': grpc.unary_unary_rpc_method_handler(
                    servicer.RefreshToken,
                    request_deserializer=bitsflea__pb2.RefreshTokenRequest.FromString,
                    response_serializer=bitsflea__pb2.RefreshTokenReply.SerializeToString,
            ),
            'Referral': grpc.unary_unary_rpc_method_handler(
                    servicer.Referral,
                    request_deserializer=bitsflea__pb2.EosidRequest.FromString,
                    response_serializer=bitsflea__pb2.BaseReply.SerializeToString,
            ),
            'Search': grpc.unary_unary_rpc_method_handler(
                    servicer.Search,
                    request_deserializer=bitsflea__pb2.SearchRequest.FromString,
                    response_serializer=bitsflea__pb2.SearchReply.SerializeToString,
            ),
            'Transaction': grpc.unary_unary_rpc_method_handler(
                    servicer.Transaction,
                    request_deserializer=bitsflea__pb2.TransactionRequest.FromString,
                    response_serializer=bitsflea__pb2.BaseReply.SerializeToString,
            ),
            'Follow': grpc.unary_unary_rpc_method_handler(
                    servicer.Follow,
                    request_deserializer=bitsflea__pb2.FollowRequest.FromString,
                    response_serializer=bitsflea__pb2.BaseReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'bitsflea.BitsFlea', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class BitsFlea(object):
    """Missing associated documentation comment in .proto file"""

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/bitsflea.BitsFlea/Register',
            bitsflea__pb2.RegisterRequest.SerializeToString,
            bitsflea__pb2.RegisterReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendSmsCode(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/bitsflea.BitsFlea/SendSmsCode',
            bitsflea__pb2.SmsRequest.SerializeToString,
            bitsflea__pb2.BaseReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RefreshToken(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/bitsflea.BitsFlea/RefreshToken',
            bitsflea__pb2.RefreshTokenRequest.SerializeToString,
            bitsflea__pb2.RefreshTokenReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Referral(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/bitsflea.BitsFlea/Referral',
            bitsflea__pb2.EosidRequest.SerializeToString,
            bitsflea__pb2.BaseReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Search(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/bitsflea.BitsFlea/Search',
            bitsflea__pb2.SearchRequest.SerializeToString,
            bitsflea__pb2.SearchReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Transaction(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/bitsflea.BitsFlea/Transaction',
            bitsflea__pb2.TransactionRequest.SerializeToString,
            bitsflea__pb2.BaseReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Follow(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/bitsflea.BitsFlea/Follow',
            bitsflea__pb2.FollowRequest.SerializeToString,
            bitsflea__pb2.BaseReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)
