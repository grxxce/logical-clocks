# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: service.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rservice.proto\x12\x0emessage_server\"#\n\x0fGetUsersRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"\x91\x01\n\x10GetUsersResponse\x12?\n\x06status\x18\x01 \x01(\x0e\x32/.message_server.GetUsersResponse.GetUsersStatus\x12\x10\n\x08username\x18\x02 \x01(\t\"*\n\x0eGetUsersStatus\x12\x0b\n\x07SUCCESS\x10\x00\x12\x0b\n\x07\x46\x41ILURE\x10\x01\"P\n\x07Message\x12\x0e\n\x06sender\x18\x01 \x01(\t\x12\x11\n\trecipient\x18\x02 \x01(\t\x12\x0f\n\x07message\x18\x03 \x01(\t\x12\x11\n\ttimestamp\x18\x04 \x01(\t\"*\n\x16MonitorMessagesRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"{\n\x0fMessageResponse\x12=\n\x06status\x18\x01 \x01(\x0e\x32-.message_server.MessageResponse.MessageStatus\")\n\rMessageStatus\x12\x0b\n\x07SUCCESS\x10\x00\x12\x0b\n\x07\x46\x41ILURE\x10\x01\")\n\x15PendingMessageRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"\xc1\x01\n\x16PendingMessageResponse\x12K\n\x06status\x18\x01 \x01(\x0e\x32;.message_server.PendingMessageResponse.PendingMessageStatus\x12(\n\x07message\x18\x02 \x01(\x0b\x32\x17.message_server.Message\"0\n\x14PendingMessageStatus\x12\x0b\n\x07SUCCESS\x10\x00\x12\x0b\n\x07\x46\x41ILURE\x10\x01\x32\xe5\x02\n\rMessageServer\x12O\n\x08GetUsers\x12\x1f.message_server.GetUsersRequest\x1a .message_server.GetUsersResponse0\x01\x12G\n\x0bSendMessage\x12\x17.message_server.Message\x1a\x1f.message_server.MessageResponse\x12\x64\n\x11GetPendingMessage\x12%.message_server.PendingMessageRequest\x1a&.message_server.PendingMessageResponse0\x01\x12T\n\x0fMonitorMessages\x12&.message_server.MonitorMessagesRequest\x1a\x17.message_server.Message0\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'service_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_GETUSERSREQUEST']._serialized_start=33
  _globals['_GETUSERSREQUEST']._serialized_end=68
  _globals['_GETUSERSRESPONSE']._serialized_start=71
  _globals['_GETUSERSRESPONSE']._serialized_end=216
  _globals['_GETUSERSRESPONSE_GETUSERSSTATUS']._serialized_start=174
  _globals['_GETUSERSRESPONSE_GETUSERSSTATUS']._serialized_end=216
  _globals['_MESSAGE']._serialized_start=218
  _globals['_MESSAGE']._serialized_end=298
  _globals['_MONITORMESSAGESREQUEST']._serialized_start=300
  _globals['_MONITORMESSAGESREQUEST']._serialized_end=342
  _globals['_MESSAGERESPONSE']._serialized_start=344
  _globals['_MESSAGERESPONSE']._serialized_end=467
  _globals['_MESSAGERESPONSE_MESSAGESTATUS']._serialized_start=426
  _globals['_MESSAGERESPONSE_MESSAGESTATUS']._serialized_end=467
  _globals['_PENDINGMESSAGEREQUEST']._serialized_start=469
  _globals['_PENDINGMESSAGEREQUEST']._serialized_end=510
  _globals['_PENDINGMESSAGERESPONSE']._serialized_start=513
  _globals['_PENDINGMESSAGERESPONSE']._serialized_end=706
  _globals['_PENDINGMESSAGERESPONSE_PENDINGMESSAGESTATUS']._serialized_start=658
  _globals['_PENDINGMESSAGERESPONSE_PENDINGMESSAGESTATUS']._serialized_end=706
  _globals['_MESSAGESERVER']._serialized_start=709
  _globals['_MESSAGESERVER']._serialized_end=1066
# @@protoc_insertion_point(module_scope)
