# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: task.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\ntask.proto\x12\x0bmarketplace\"6\n\x15RegisterSellerRequest\x12\x0f\n\x07ip_port\x18\x01 \x01(\t\x12\x0c\n\x04uuid\x18\x02 \x01(\t\"w\n\x16RegisterSellerResponse\x12:\n\x06status\x18\x01 \x01(\x0e\x32*.marketplace.RegisterSellerResponse.Status\"!\n\x06Status\x12\x0b\n\x07SUCCESS\x10\x00\x12\n\n\x06\x46\x41ILED\x10\x01\"\xc3\x01\n\x0fSellItemRequest\x12\x14\n\x0cproduct_name\x18\x01 \x01(\t\x12.\n\x08\x63\x61tegory\x18\x02 \x01(\x0e\x32\x1c.marketplace.ProductCategory\x12\x10\n\x08quantity\x18\x03 \x01(\x05\x12\x13\n\x0b\x64\x65scription\x18\x04 \x01(\t\x12\x16\n\x0eseller_address\x18\x05 \x01(\t\x12\x13\n\x0bseller_uuid\x18\x06 \x01(\t\x12\x16\n\x0eprice_per_unit\x18\x07 \x01(\x02\"\x8d\x01\n\x10SellItemResponse\x12\x34\n\x06status\x18\x01 \x01(\x0e\x32$.marketplace.SellItemResponse.Status\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0f\n\x07item_id\x18\x03 \x01(\x05\"!\n\x06Status\x12\x0b\n\x07SUCCESS\x10\x00\x12\n\n\x06\x46\x41ILED\x10\x01*;\n\x0fProductCategory\x12\x0f\n\x0b\x45LECTRONICS\x10\x00\x12\x0b\n\x07\x46\x41SHION\x10\x01\x12\n\n\x06OTHERS\x10\x02\x32\xac\x01\n\x06Market\x12Y\n\x0eRegisterSeller\x12\".marketplace.RegisterSellerRequest\x1a#.marketplace.RegisterSellerResponse\x12G\n\x08SellItem\x12\x1c.marketplace.SellItemRequest\x1a\x1d.marketplace.SellItemResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'task_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_PRODUCTCATEGORY']._serialized_start=546
  _globals['_PRODUCTCATEGORY']._serialized_end=605
  _globals['_REGISTERSELLERREQUEST']._serialized_start=27
  _globals['_REGISTERSELLERREQUEST']._serialized_end=81
  _globals['_REGISTERSELLERRESPONSE']._serialized_start=83
  _globals['_REGISTERSELLERRESPONSE']._serialized_end=202
  _globals['_REGISTERSELLERRESPONSE_STATUS']._serialized_start=169
  _globals['_REGISTERSELLERRESPONSE_STATUS']._serialized_end=202
  _globals['_SELLITEMREQUEST']._serialized_start=205
  _globals['_SELLITEMREQUEST']._serialized_end=400
  _globals['_SELLITEMRESPONSE']._serialized_start=403
  _globals['_SELLITEMRESPONSE']._serialized_end=544
  _globals['_SELLITEMRESPONSE_STATUS']._serialized_start=169
  _globals['_SELLITEMRESPONSE_STATUS']._serialized_end=202
  _globals['_MARKET']._serialized_start=608
  _globals['_MARKET']._serialized_end=780
# @@protoc_insertion_point(module_scope)
