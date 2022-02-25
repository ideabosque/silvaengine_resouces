#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

from silvaengine_utility import Utility
from pynamodb.connection import Connection
from pynamodb.transactions import TransactWrite
from pynamodb.exceptions import TransactWriteError
from datetime import datetime
from importlib.util import find_spec
from importlib import import_module
from hashlib import md5
from .models import (
    ResourceModel,
    FunctionsModel,
    ConfigDataModel,
    ConnectionsModel,
)
from .enumerations import SwitchStatus
import boto3


__author__ = "bl"


def _get_operations(payload, returnMap=False) -> list:
    operations = []

    if type(payload) is list and len(payload):
        attributes = ["label", "action"] if returnMap else ["action"]
        al = len(attributes)

        for item in payload:
            if al == 1:
                operations += [item[k] for k in item.keys if k in attributes]
            else:
                pairs = {k: item[k] for k in item.keys() if k in attributes}

                if len(pairs.keys()) == al:
                    operations.append(pairs)

    return operations


def add_resource_handler(cloud_function_name, apply_to, packages):
    try:
        if (
            not cloud_function_name
            or not apply_to
            or type(packages) is not list
            or len(packages) < 1
        ):
            return

        identity = boto3.client(
            "sts",
            region_name=ResourceModel.Meta.region,
            aws_access_key_id=ResourceModel.Meta.aws_access_key_id,
            aws_secret_access_key=ResourceModel.Meta.aws_secret_access_key,
        ).get_caller_identity()

        if identity.get("Account") is None:
            return

        statements = []

        # Deploy area
        area = ResourceModel.Meta.aws_api_area
        # endpoint_id = ResourceModel.Meta.aws_endpoint_id

        # TODO: Get region / IAM Number from env.
        aws_lambda_arn = "arn:aws:lambda:{}:{}:function:{}".format(
            ResourceModel.Meta.region,
            identity.get("Account"),
            str(cloud_function_name).strip(),
        )
        now = datetime.utcnow()
        mutation_actions = ["create", "update", "delete", "mutation"]

        # Insert resource / function / config data.
        for package in packages:
            # 1. Load module by dynamic
            fn_deploy = Utility.import_dynamically(
                module_name=package, function_name="deploy"
            )

            if not callable(fn_deploy):
                continue

            profiles = fn_deploy()

            if type(profiles) is not list or len(profiles) < 1:
                continue

            # 2. Insert resource / function.
            for profile in profiles:
                class_name = profile.get("class")

                if not class_name:
                    continue

                service = str(profile.get("service", package)).strip()

                for function_name, config in profile.get("functions", []).items():
                    function_name = str(function_name).strip()
                    # Factor of generate resource ID
                    factor = "{}-{}-{}".format(
                        str(package).strip(),
                        str(profile.get("class", "")).strip(),
                        function_name,
                    ).lower()
                    resource_id = md5(factor.encode(encoding="UTF-8")).hexdigest()
                    mutations = []

                    for action in mutation_actions:
                        mutations += _get_operations(config.get(action), True)

                    try:
                        ResourceModel(resource_id, service).delete()
                    except:
                        pass

                    # 2.1 Add new resource to table se-resource
                    if not config.get("disabled_in_resources", False):
                        statements.append(
                            {
                                "statement": ResourceModel(
                                    resource_id,
                                    service,
                                    **{
                                        "apply_to": apply_to,
                                        "module_name": str(package).strip(),
                                        "class_name": str(class_name).strip(),
                                        "function": function_name,
                                        "label": str(config.get("label", "")).strip(),
                                        "status": SwitchStatus.YES.value,
                                        "operations": {
                                            "mutation": mutations,
                                            "query": _get_operations(
                                                config.get("query"), True
                                            ),
                                        },
                                        "created_at": now,
                                        "updated_at": now,
                                        # "updated_by": updated_by,
                                    },
                                ),
                                # "condition": ResourceModel.resource_id != resource_id,
                            }
                        )

                    # 2.2 Add new function to table se-functions
                    mutations = []

                    for action in mutation_actions:
                        mutations += _get_operations(config.get(action))

                    statements.append(
                        {
                            "statement": FunctionsModel(
                                aws_lambda_arn,
                                function_name,
                                **{
                                    "area": str(area).strip() if area else "",
                                    "config": {
                                        "class_name": str(class_name).strip(),
                                        "funct_type": config.get(
                                            "type", "RequestResponse"
                                        ),
                                        "methods": config.get("support_methods")
                                        if type(config.get("support_methods")) is list
                                        and len(config.get("support_methods"))
                                        else ["POST", "GET"],
                                        "module_name": str(package).strip(),
                                        "setting": config.get("settings", package),
                                        "auth_required": bool(
                                            config.get("is_auth_required", False)
                                        ),
                                        "graphql": bool(config.get("is_graphql", True)),
                                        "operations": {
                                            "mutation": list(set(mutations)),
                                            "query": _get_operations(
                                                config.get("query")
                                            ),
                                        },
                                    },
                                },
                            ),
                            # "condition": FunctionsModel.function.does_not_exist(),
                        }
                    )

                    # 2.3 Add function setting to se-connections
                    for connection in ConnectionsModel.query(apply_to):
                        functions = connection.functions

                        if len(
                            item.function
                            for item in functions
                            if item.function == function_name
                        ):
                            continue

                        functions.append(
                            {
                                "aws_lambda_arn": aws_lambda_arn,
                                "function": function_name,
                                "setting": "",
                            }
                        )

                        statements.append(
                            {
                                "statement": ConnectionsModel(
                                    apply_to,
                                    connection.api_key,
                                    **{
                                        "functions": functions,
                                    },
                                ),
                            }
                        )

        # Insert by batch
        if len(statements):
            print("Start setting configuration information: ")
            # @TODO: If statements total more than 25, should use batchWrite to replace.
            # with TransactWrite(
            #     connection=Connection(region=ResourceModel.Meta.region),
            #     client_request_token=uuid.uuid1().hex,
            # ) as transaction:
            for item in statements:
                if not item.get("statement"):
                    continue

                item.get("statement").save()

                # if item.get("condition"):
                #     transaction.save(
                #         item.get("statement"), condition=(item.get("condition"))
                #     )
                # else:
                #     transaction.save(item.get("statement"))

                print("Completed:", item.get("statement"))

        print("Done!")
    except Exception as e:
        raise e
