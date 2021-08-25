#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function


__author__ = "bl"

from graphene import ObjectType, InputObjectType, String, DateTime, Int, List, Field
from silvaengine_utility import JSON


class ResourceOperationItemMap(ObjectType):
    label = String()
    action = String()


class ResourceOperationMap(ObjectType):
    query = List(ResourceOperationItemMap)
    mutation = List(ResourceOperationItemMap)


class ResourceType(ObjectType):
    resource_id = String()
    service = String()
    module_name = String()
    class_name = String()
    function = String()
    operations = Field(ResourceOperationMap)
    label = String()
    status = Int()
    created_at = DateTime()
    updated_at = DateTime()
    updated_by = String()


class PageInputType(InputObjectType):
    hash_key = String()
    range_key = String()


class ResourcesType(ObjectType):
    items = List(ResourceType)
    last_evaluated_key = JSON()


class ResourceInputType(InputObjectType):
    resource_id = String()
    service = String()
    module_name = String()
    class_name = String()
    function = String()
    label = String()
    status = Int()
    updated_by = String()
