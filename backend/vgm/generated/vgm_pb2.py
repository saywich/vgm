from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    7,
    35,
    1,
    '',
    'vgm.proto'
)


_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\tvgm.proto\x12\x03vgm\"\x17\n\x07Payload\x12\x0c\n\x04json\x18\x01 \x01(\t2\xa4\x02\n\x08Identity\x12&\n\x08Register\x12\x0c.vgm.Payload\x1a\x0c.vgm.Payload\x12#\n\x05Login\x12\x0c.vgm.Payload\x1a\x0c.vgm.Payload\x12*\n\x0c\x41uthenticate\x12\x0c.vgm.Payload\x1a\x0c.vgm.Payload\x12$\n\x06Logout\x12\x0c.vgm.Payload\x1a\x0c.vgm.Payload\x12$\n\x06Search\x12\x0c.vgm.Payload\x1a\x0c.vgm.Payload\x12&\n\x08Profiles\x12\x0c.vgm.Payload\x1a\x0c.vgm.Payload\x12+\n\rUpdateProfile\x12\x0c.vgm.Payload\x1a\x0c.vgm.Payload2\xb4\x01\n\tMessaging\x12+\n\rConversations\x12\x0c.vgm.Payload\x1a\x0c.vgm.Payload\x12.\n\x10OpenConversation\x12\x0c.vgm.Payload\x1a\x0c.vgm.Payload\x12&\n\x08Messages\x12\x0c.vgm.Payload\x1a\x0c.vgm.Payload\x12\"\n\x04Send\x12\x0c.vgm.Payload\x1a\x0c.vgm.Payload2.\n\x05Video\x12%\n\x07Resolve\x12\x0c.vgm.Payload\x1a\x0c.vgm.Payloadb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'vgm_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_PAYLOAD']._serialized_start=18
  _globals['_PAYLOAD']._serialized_end=41
  _globals['_IDENTITY']._serialized_start=44
  _globals['_IDENTITY']._serialized_end=336
  _globals['_MESSAGING']._serialized_start=339
  _globals['_MESSAGING']._serialized_end=519
  _globals['_VIDEO']._serialized_start=521
  _globals['_VIDEO']._serialized_end=567

