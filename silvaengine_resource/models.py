#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bl"

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
        aws_access_key_id = os.getenv("aws_access_key_id")
        aws_secret_access_key = os.getenv("aws_secret_access_key")
        aws_api_area = os.getenv("aws_api_area", "core")
        aws_endpoint_id = os.getenv("aws_endpoint_id", "api")

        if region is None or aws_access_key_id is None or aws_secret_access_key is None:
            from dotenv import load_dotenv

            if load_dotenv():
                if region is None:
                    region = os.getenv("region_name")

                if aws_access_key_id is None:
                    aws_access_key_id = os.getenv("aws_access_key_id")

                if aws_secret_access_key is None:
                    aws_secret_access_key = os.getenv("aws_secret_access_key")


class ResourceOperationItemMap(MapAttribute):
    label = UnicodeAttribute()
    action = UnicodeAttribute()


class ResourceOperationMap(MapAttribute):
    # create = ListAttribute(of=ResourceOperationItemMap)
    query = ListAttribute(of=ResourceOperationItemMap)
    mutation = ListAttribute(of=ResourceOperationItemMap)
    # update = ListAttribute(of=ResourceOperationItemMap)
    # delete = ListAttribute(of=ResourceOperationItemMap)


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
    operations = ResourceOperationMap()
    created_at = UTCDateTimeAttribute()
    updated_at = UTCDateTimeAttribute()
    updated_by = UnicodeAttribute(default="Setup")


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

    endpoint_id = UnicodeAttribute(hash_key=True)
    api_key = UnicodeAttribute(range_key=True, default="#####")
    functions = ListAttribute(of=FunctionMap)
    whitelist = ListAttribute()


class OperationMap(MapAttribute):
    # create = ListAttribute()
    query = ListAttribute()
    mutation = ListAttribute()
    # update = ListAttribute()
    # delete = ListAttribute()


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
