#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bl"

from graphene import ObjectType, String, Int, List, Schema
from .types import (
    ResourceType,
)
from .queries import resolve_resources


def type_class():
    return [ResourceType]


# Query resource or role list
class Query(ObjectType):
    resources = List(
        ResourceType,
        limit=Int(),
        last_evaluated_key=String(),
        resource_id=String(),
    )

    def resolve_resources(self, info, **kwargs):
        return resolve_resources(info, **kwargs)


# Generate API documents.
def graphql_schema_doc():
    from graphdoc import to_doc

    schema = Schema(
        query=Query,
        types=type_class(),
    )

    return to_doc(schema)
