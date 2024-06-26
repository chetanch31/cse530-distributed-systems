# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import master_pb2 as master__pb2


class MasterStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.MapperInput = channel.unary_unary(
                '/master.Master/MapperInput',
                request_serializer=master__pb2.MapperInputRequest.SerializeToString,
                response_deserializer=master__pb2.MapperInputResponse.FromString,
                )
        self.ReducerInput = channel.unary_unary(
                '/master.Master/ReducerInput',
                request_serializer=master__pb2.ReducerInputRequest.SerializeToString,
                response_deserializer=master__pb2.ReducerInputResponse.FromString,
                )
        self.RequestPartition = channel.unary_unary(
                '/master.Master/RequestPartition',
                request_serializer=master__pb2.DataPointRequest.SerializeToString,
                response_deserializer=master__pb2.DataPointResponse.FromString,
                )


class MasterServicer(object):
    """Missing associated documentation comment in .proto file."""

    def MapperInput(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReducerInput(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RequestPartition(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MasterServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'MapperInput': grpc.unary_unary_rpc_method_handler(
                    servicer.MapperInput,
                    request_deserializer=master__pb2.MapperInputRequest.FromString,
                    response_serializer=master__pb2.MapperInputResponse.SerializeToString,
            ),
            'ReducerInput': grpc.unary_unary_rpc_method_handler(
                    servicer.ReducerInput,
                    request_deserializer=master__pb2.ReducerInputRequest.FromString,
                    response_serializer=master__pb2.ReducerInputResponse.SerializeToString,
            ),
            'RequestPartition': grpc.unary_unary_rpc_method_handler(
                    servicer.RequestPartition,
                    request_deserializer=master__pb2.DataPointRequest.FromString,
                    response_serializer=master__pb2.DataPointResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'master.Master', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Master(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def MapperInput(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/master.Master/MapperInput',
            master__pb2.MapperInputRequest.SerializeToString,
            master__pb2.MapperInputResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ReducerInput(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/master.Master/ReducerInput',
            master__pb2.ReducerInputRequest.SerializeToString,
            master__pb2.ReducerInputResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RequestPartition(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/master.Master/RequestPartition',
            master__pb2.DataPointRequest.SerializeToString,
            master__pb2.DataPointResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
