#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional, Union

from graphene import Schema
from silvaengine_utility import Serializer, Utility

from .resource.handlers import add_resource_handler
from .resource.schema import Query, type_class

__author__ = "bl"


# Hook function applied to deployment
def deploy() -> List[Dict[str, Any]]:
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
    def __init__(self, logger: Any, **setting: Dict[str, Any]):
        self.logger = logger
        self.setting = setting

    @staticmethod
    def add_resource(
        cloud_function_name: str, apply_to: str, area: str, packages: List
    ) -> Any:
        return add_resource_handler(
            str(cloud_function_name).strip(),
            str(apply_to).strip(),
            str(area).strip(),
            list(set(packages)),
        )

    def resource_graphql(self, **params: Dict[str, Any]) -> str:
        try:
            channel = params.get("endpoint_id", "api")

            if not channel:
                response = {
                    "errors": "Unrecognized request origin.",
                    "status_code": 401,
                }
                return Serializer.json_dumps(response)

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
                return Serializer.json_dumps(response)

            execution_result = schema.execute(
                operations, context_value=context, variable_values=variables
            )

            if not execution_result:
                response = {
                    "errors": "Invalid execution result.",
                    "status_code": 500,
                }
            elif execution_result.errors:
                response = {
                    "errors": [
                        Utility.format_error(e) for e in execution_result.errors
                    ],
                    "status_code": 400,
                }
            elif execution_result.invalid:
                response = {
                    "errors": "Invalid GraphQL query.",
                    "status_code": 400,
                }
            elif execution_result.data:
                response = {"data": execution_result.data, "status_code": 200}
            else:
                response = {
                    "errors": "Uncaught execution error.",
                    "status_code": 500,
                }

            return Serializer.json_dumps(response)
        except Exception as e:
            # Log the full error for debugging
            self.logger.error(f"GraphQL execution error: {str(e)}", exc_info=True)
            # Return a generic error message to the client
            response = {
                "errors": "Internal server error.",
                "status_code": 500,
            }
            return Serializer.json_dumps(response)
