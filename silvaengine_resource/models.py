#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import os
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    UTCDateTimeAttribute,
    NumberAttribute,
    MapAttribute,
    ListAttribute,
    BooleanAttribute,
)

# Preset resource status
class Status:
    enabled = 1


class BaseModel(Model):
    class Meta:
        billing_mode = "PAY_PER_REQUEST"
        region = os.getenv("REGIONNAME")

        if not region:
            from dotenv import load_dotenv

            load_dotenv()

            region = os.getenv("region_name")
            aws_access_key_id = os.getenv("aws_access_key_id")
            aws_secret_access_key = os.getenv("aws_secret_access_key")


class ResourceModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "se-resources"

    resource_id = UnicodeAttribute(hash_key=True)
    service = UnicodeAttribute(range_key=True)
    module_name = UnicodeAttribute()
    class_name = UnicodeAttribute()
    function = UnicodeAttribute()
    label = UnicodeAttribute()
    status = NumberAttribute()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    updated_by = UnicodeAttribute()


class ConfigDataModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "se-configdata"

    setting_id = UnicodeAttribute(hash_key=True)
    variable = UnicodeAttribute(range_key=True)
    value = UnicodeAttribute()


class EndpointsModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "se-endpoints"

    endpoint_id = UnicodeAttribute(hash_key=True)
    special_connection = BooleanAttribute(default=False)


class FunctionMap(MapAttribute):
    aws_lambda_arn = UnicodeAttribute()
    function = UnicodeAttribute()
    setting = UnicodeAttribute()


class ConnectionsModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "se-connections"

    api_key = UnicodeAttribute(hash_key=True)
    endpoint_id = UnicodeAttribute(range_key=True, default="#####")
    functions = ListAttribute(of=FunctionMap)


class OperationMap(MapAttribute):
    create = ListAttribute()
    query = ListAttribute()
    update = ListAttribute()
    delete = ListAttribute()


class ConfigMap(MapAttribute):
    class_name = UnicodeAttribute()
    funct_type = UnicodeAttribute()
    methods = ListAttribute()
    module_name = UnicodeAttribute()
    setting = UnicodeAttribute()
    auth_required = BooleanAttribute(default=False)
    graphql = BooleanAttribute(default=False)
    operations = OperationMap()


class FunctionsModel(BaseModel):
    class Meta(BaseModel.Meta):
        table_name = "se-functions"

    aws_lambda_arn = UnicodeAttribute(hash_key=True)
    function = UnicodeAttribute(range_key=True)
    area = UnicodeAttribute()
    config = ConfigMap()
