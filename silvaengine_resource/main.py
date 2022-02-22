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
        try:
            schema = Schema(
                query=Query,
                types=type_class(),
            )
            context = {"logger": self.logger}
            variables = params.get("variables", {})
            operations = params.get("query")
            response = {
                "errors": "Invalid operations.",
                "status_code": 400,
            }

            if not operations:
                return Utility.json_dumps(response)

            execution_result = schema.execute(
                operations, context_value=context, variable_values=variables
            )

            if not execution_result:
                response = {
                    "errors": "Invalid execution result.",
                }
            elif execution_result.errors:
                response = {
                    "errors": [
                        Utility.format_error(e) for e in execution_result.errors
                    ],
                }
            elif execution_result.invalid:
                response = execution_result
            elif execution_result.data:
                response = {"data": execution_result.data, "status_code": 200}
            else:
                response = {
                    "errors": "Uncaught execution error.",
                }

            return Utility.json_dumps(response)
        except Exception as e:
            raise e
