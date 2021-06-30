#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bl"

from graphene import (
    ObjectType,
    InputObjectType,
    String,
    DateTime,
    Int,
)


class ResourceType(ObjectType):
    resource_id = String()
    service = String()
    module_name = String()
    class_name = String()
    function = String()
    label = String()
    status = Int()
    created_at = DateTime()
    updated_at = DateTime()
    updated_by = String()
    last_evaluated_key = String()


class ResourceInputType(InputObjectType):
    resource_id = String()
    service = String()
    module_name = String()
    class_name = String()
    function = String()
    label = String()
    status = Int()
    updated_by = String()
