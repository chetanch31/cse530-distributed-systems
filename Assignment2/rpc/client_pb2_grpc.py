# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import client_pb2 as client__pb2


class clientStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ServeClient = channel.unary_unary(
                '/client.client/ServeClient',
                request_serializer=client__pb2.ServeClientArgs.SerializeToString,
                response_deserializer=client__pb2.ServeClientReply.FromString,
                )


class clientServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ServeClient(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_clientServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ServeClient': grpc.unary_unary_rpc_method_handler(
                    servicer.ServeClient,
                    request_deserializer=client__pb2.ServeClientArgs.FromString,
                    response_serializer=client__pb2.ServeClientReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'client.client', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class client(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ServeClient(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/client.client/ServeClient',
            client__pb2.ServeClientArgs.SerializeToString,
            client__pb2.ServeClientReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
