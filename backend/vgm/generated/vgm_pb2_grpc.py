import grpc
import warnings

from . import vgm_pb2 as vgm__pb2

GRPC_GENERATED_VERSION = '1.85.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + ' but the generated code in vgm_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class IdentityStub:
    

    def __init__(self, channel):
        
        self.Register = channel.unary_unary(
                '/vgm.Identity/Register',
                request_serializer=vgm__pb2.Payload.SerializeToString,
                response_deserializer=vgm__pb2.Payload.FromString,
                _registered_method=True)
        self.Login = channel.unary_unary(
                '/vgm.Identity/Login',
                request_serializer=vgm__pb2.Payload.SerializeToString,
                response_deserializer=vgm__pb2.Payload.FromString,
                _registered_method=True)
        self.Authenticate = channel.unary_unary(
                '/vgm.Identity/Authenticate',
                request_serializer=vgm__pb2.Payload.SerializeToString,
                response_deserializer=vgm__pb2.Payload.FromString,
                _registered_method=True)
        self.Logout = channel.unary_unary(
                '/vgm.Identity/Logout',
                request_serializer=vgm__pb2.Payload.SerializeToString,
                response_deserializer=vgm__pb2.Payload.FromString,
                _registered_method=True)
        self.Search = channel.unary_unary(
                '/vgm.Identity/Search',
                request_serializer=vgm__pb2.Payload.SerializeToString,
                response_deserializer=vgm__pb2.Payload.FromString,
                _registered_method=True)
        self.Profiles = channel.unary_unary(
                '/vgm.Identity/Profiles',
                request_serializer=vgm__pb2.Payload.SerializeToString,
                response_deserializer=vgm__pb2.Payload.FromString,
                _registered_method=True)
        self.UpdateProfile = channel.unary_unary(
                '/vgm.Identity/UpdateProfile',
                request_serializer=vgm__pb2.Payload.SerializeToString,
                response_deserializer=vgm__pb2.Payload.FromString,
                _registered_method=True)


class IdentityServicer:
    

    def Register(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Login(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Authenticate(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Logout(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Search(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Profiles(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateProfile(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_IdentityServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Register': grpc.unary_unary_rpc_method_handler(
                    servicer.Register,
                    request_deserializer=vgm__pb2.Payload.FromString,
                    response_serializer=vgm__pb2.Payload.SerializeToString,
            ),
            'Login': grpc.unary_unary_rpc_method_handler(
                    servicer.Login,
                    request_deserializer=vgm__pb2.Payload.FromString,
                    response_serializer=vgm__pb2.Payload.SerializeToString,
            ),
            'Authenticate': grpc.unary_unary_rpc_method_handler(
                    servicer.Authenticate,
                    request_deserializer=vgm__pb2.Payload.FromString,
                    response_serializer=vgm__pb2.Payload.SerializeToString,
            ),
            'Logout': grpc.unary_unary_rpc_method_handler(
                    servicer.Logout,
                    request_deserializer=vgm__pb2.Payload.FromString,
                    response_serializer=vgm__pb2.Payload.SerializeToString,
            ),
            'Search': grpc.unary_unary_rpc_method_handler(
                    servicer.Search,
                    request_deserializer=vgm__pb2.Payload.FromString,
                    response_serializer=vgm__pb2.Payload.SerializeToString,
            ),
            'Profiles': grpc.unary_unary_rpc_method_handler(
                    servicer.Profiles,
                    request_deserializer=vgm__pb2.Payload.FromString,
                    response_serializer=vgm__pb2.Payload.SerializeToString,
            ),
            'UpdateProfile': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateProfile,
                    request_deserializer=vgm__pb2.Payload.FromString,
                    response_serializer=vgm__pb2.Payload.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'vgm.Identity', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('vgm.Identity', rpc_method_handlers)


 
class Identity:
    

    @staticmethod
    def Register(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/vgm.Identity/Register',
            vgm__pb2.Payload.SerializeToString,
            vgm__pb2.Payload.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Login(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/vgm.Identity/Login',
            vgm__pb2.Payload.SerializeToString,
            vgm__pb2.Payload.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Authenticate(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/vgm.Identity/Authenticate',
            vgm__pb2.Payload.SerializeToString,
            vgm__pb2.Payload.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Logout(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/vgm.Identity/Logout',
            vgm__pb2.Payload.SerializeToString,
            vgm__pb2.Payload.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Search(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/vgm.Identity/Search',
            vgm__pb2.Payload.SerializeToString,
            vgm__pb2.Payload.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Profiles(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/vgm.Identity/Profiles',
            vgm__pb2.Payload.SerializeToString,
            vgm__pb2.Payload.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def UpdateProfile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/vgm.Identity/UpdateProfile',
            vgm__pb2.Payload.SerializeToString,
            vgm__pb2.Payload.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)


class MessagingStub:
    

    def __init__(self, channel):
        
        self.Conversations = channel.unary_unary(
                '/vgm.Messaging/Conversations',
                request_serializer=vgm__pb2.Payload.SerializeToString,
                response_deserializer=vgm__pb2.Payload.FromString,
                _registered_method=True)
        self.OpenConversation = channel.unary_unary(
                '/vgm.Messaging/OpenConversation',
                request_serializer=vgm__pb2.Payload.SerializeToString,
                response_deserializer=vgm__pb2.Payload.FromString,
                _registered_method=True)
        self.Messages = channel.unary_unary(
                '/vgm.Messaging/Messages',
                request_serializer=vgm__pb2.Payload.SerializeToString,
                response_deserializer=vgm__pb2.Payload.FromString,
                _registered_method=True)
        self.Send = channel.unary_unary(
                '/vgm.Messaging/Send',
                request_serializer=vgm__pb2.Payload.SerializeToString,
                response_deserializer=vgm__pb2.Payload.FromString,
                _registered_method=True)


class MessagingServicer:
    

    def Conversations(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def OpenConversation(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Messages(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Send(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MessagingServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Conversations': grpc.unary_unary_rpc_method_handler(
                    servicer.Conversations,
                    request_deserializer=vgm__pb2.Payload.FromString,
                    response_serializer=vgm__pb2.Payload.SerializeToString,
            ),
            'OpenConversation': grpc.unary_unary_rpc_method_handler(
                    servicer.OpenConversation,
                    request_deserializer=vgm__pb2.Payload.FromString,
                    response_serializer=vgm__pb2.Payload.SerializeToString,
            ),
            'Messages': grpc.unary_unary_rpc_method_handler(
                    servicer.Messages,
                    request_deserializer=vgm__pb2.Payload.FromString,
                    response_serializer=vgm__pb2.Payload.SerializeToString,
            ),
            'Send': grpc.unary_unary_rpc_method_handler(
                    servicer.Send,
                    request_deserializer=vgm__pb2.Payload.FromString,
                    response_serializer=vgm__pb2.Payload.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'vgm.Messaging', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('vgm.Messaging', rpc_method_handlers)


 
class Messaging:
    

    @staticmethod
    def Conversations(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/vgm.Messaging/Conversations',
            vgm__pb2.Payload.SerializeToString,
            vgm__pb2.Payload.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def OpenConversation(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/vgm.Messaging/OpenConversation',
            vgm__pb2.Payload.SerializeToString,
            vgm__pb2.Payload.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Messages(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/vgm.Messaging/Messages',
            vgm__pb2.Payload.SerializeToString,
            vgm__pb2.Payload.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Send(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/vgm.Messaging/Send',
            vgm__pb2.Payload.SerializeToString,
            vgm__pb2.Payload.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)


class VideoStub:
    

    def __init__(self, channel):
        
        self.Resolve = channel.unary_unary(
                '/vgm.Video/Resolve',
                request_serializer=vgm__pb2.Payload.SerializeToString,
                response_deserializer=vgm__pb2.Payload.FromString,
                _registered_method=True)


class VideoServicer:
    

    def Resolve(self, request, context):
        
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_VideoServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Resolve': grpc.unary_unary_rpc_method_handler(
                    servicer.Resolve,
                    request_deserializer=vgm__pb2.Payload.FromString,
                    response_serializer=vgm__pb2.Payload.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'vgm.Video', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('vgm.Video', rpc_method_handlers)


 
class Video:
    

    @staticmethod
    def Resolve(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/vgm.Video/Resolve',
            vgm__pb2.Payload.SerializeToString,
            vgm__pb2.Payload.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
