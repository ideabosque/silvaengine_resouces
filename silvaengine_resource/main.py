#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bl"

from graphene import Schema
from silvaengine_utility import Utility
from .resource.handlers import add_resource_handler
from .resource.schema import Query, type_class

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
                    "settings": "beta_core_api",
                    "disabled_in_resources": True,  # Ignore adding to resource list.
                }
            },
        }
    ]


class Resource(object):
    def __init__(self, logger, **setting):
        self.logger = logger
        self.setting = setting

    @staticmethod
    def add_resource(cloud_function_name, apply_to, packages):
        return add_resource_handler(
            str(cloud_function_name).strip(), str(apply_to).strip(), list(set(packages))
        )

    def resource_graphql(self, **params):
        try:
            channel = params.get("endpoint_id", "api")

            if not channel:
                raise Exception("Unrecognized request origin", 401)

            context = {
                "logger": self.logger,
                "setting": self.setting,
                "context": params.get("context", {}),
                "channel": str(channel).strip(),
            }
            schema = Schema(query=Query, types=type_class())
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
