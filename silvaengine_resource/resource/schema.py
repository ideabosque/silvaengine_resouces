#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Any, List

from graphene import Field, Int, ObjectType, Schema, String
from silvaengine_utility import JSONCamelCase

from .queries import resolve_resources
from .types import ResourcesType

__author__ = "bl"


def type_class() -> List[Any]:
    return [ResourcesType]


# Query resource or role list
class Query(ObjectType):
    resources = Field(
        ResourcesType,
        limit=Int(),
        # last_evaluated_key=JSON(),
        resource_id=String(),
    )

    def resolve_resources(self, info, **kwargs):
        return resolve_resources(info, **kwargs)


# Generate API documents.
def graphql_schema_doc() -> Any:
    from graphdoc import to_doc

    schema = Schema(
        query=Query,
        types=type_class(),
    )

    return to_doc(schema)
