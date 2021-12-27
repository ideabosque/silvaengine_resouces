#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bl"

from graphene import Schema
from silvaengine_utility import Utility
from .handlers import _add_resource_handler
from .schema import Query, type_class

# Hook function applied to deployment
def deploy() -> list:
    return [
        {
            "service": "resources",
            "class": "Resource",
            "functions": {
                "resource_graphql": {
                    "is_static": False,
                    "label": "Resources",
                    "query": [
                        {
                            "action": "resources",
                            "label": "Query Resources",
                        },
                    ],
                    "type": "RequestResponse",
                    "support_methods": ["POST"],
                    "is_auth_required": False,
                    "is_graphql": True,
                    "disabled_in_resources": True,
                }
            },
        }
    ]


class Resource(object):
    def __init__(self, logger, **setting):
        self.logger = logger
        self.setting = setting

    @staticmethod
    def add_resource(packages):
        return _add_resource_handler(packages)

    def resource_graphql(self, **params):
        schema = Schema(
            query=Query,
            types=type_class(),
        )
        ctx = {"logger": self.logger}
        variables = params.get("variables", {})
        query = params.get("query")

        if query is not None:
            execution_result = schema.execute(
                query, context_value=ctx, variable_values=variables
            )

        mutation = params.get("mutation")

        if mutation is not None:
            execution_result = schema.execute(
                mutation, context_value=ctx, variable_values=variables
            )

        if not execution_result:
            return None

        status_code = 400 if execution_result.invalid else 200

        if execution_result.errors:
            return Utility.json_dumps(
                {
                    "errors": [
                        Utility.format_error(e) for e in execution_result.errors
                    ],
                    "status_code": 500,
                }
            )

        return Utility.json_dumps(
            {
                "data": execution_result.data,
                "status_code": status_code,
            }
        )
