#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from graphene import ObjectType, String, Int, Schema, Field
from silvaengine_utility import JSON
from .types import ResourcesType
from .queries import resolve_resources

__author__ = "bl"


def type_class():
    return [ResourcesType]


# Query resource or role list
class Query(ObjectType):
    resources = Field(
        ResourcesType,
        limit=Int(),
        last_evaluated_key=JSON(),
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
