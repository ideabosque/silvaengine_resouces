#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from silvaengine_utility import Utility
from datetime import datetime
from dotenv import load_dotenv
from hashlib import md5
from silvaengine_resource.resource.models import (
    ResourceModel,
    FunctionsModel,
    ConnectionsModel,
    FunctionMap,
)
from silvaengine_resource.resource.enumerations import SwitchStatus
import boto3, os, copy


__author__ = "bl"


def _get_operations(payload, return_as_map=False) -> list:
    operations = []

    if type(payload) is list and len(payload):
        required_attributes = ["label", "action"]
        attributes = required_attributes + ["visible"] if return_as_map else ["action"]
        al = len(attributes)

        for item in payload:
            if al == 1:
                operations += [item[k] for k in item.keys() if k in attributes]
            else:
                pairs = {k: item[k] for k in item.keys() if k in attributes}

                if len(
                    list(set(required_attributes).intersection(set(pairs.keys())))
                ) == len(required_attributes):
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
        connection_functions = {}

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
                    factor = (
                        "{module_name}-{class_name}-{function_name}-{channel}".format(
                            module_name=str(package).strip(),
                            class_name=str(profile.get("class", "")).strip(),
                            function_name=function_name,
                            channel=str(apply_to).strip(),
                        ).lower()
                    )
                    resource_id = md5(factor.encode(encoding="UTF-8")).hexdigest()

                    try:
                        ResourceModel(resource_id, service).delete()
                    except:
                        pass

                    # 2.1 Add new resource to table se-resource
                    if not config.get("disabled_in_resources", False):
                        queries = _get_operations(
                            payload=config.get("query"),
                            return_as_map=True,
                        )
                        mutations = []

                        for action in mutation_actions:
                            mutations += _get_operations(
                                payload=config.get(action),
                                return_as_map=True,
                            )

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
                                            "query": queries,
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
                    support_methods = (
                        config.get("support_methods")
                        if type(config.get("support_methods")) is list
                        and len(config.get("support_methods"))
                        else ["POST", "GET"]
                    )
                    queries = _get_operations(payload=config.get("query"))
                    mutations = []

                    for action in mutation_actions:
                        mutations += _get_operations(payload=config.get(action))

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
                                        "methods": support_methods,
                                        "module_name": str(package).strip(),
                                        "setting": config.get("settings", package),
                                        "auth_required": bool(
                                            config.get("is_auth_required", False)
                                        ),
                                        "graphql": bool(config.get("is_graphql", True)),
                                        "operations": {
                                            "mutation": list(set(mutations)),
                                            "query": list(set(queries)),
                                        },
                                    },
                                },
                            ),
                            # "condition": FunctionsModel.function.does_not_exist(),
                        }
                    )

                    # 2.3 Build function list for connections.
                    connection_functions[function_name.lower()] = FunctionMap(
                        **{
                            "aws_lambda_arn": aws_lambda_arn,
                            "function": function_name,
                            "setting": "",
                        }
                    )

        # 2.3 Add function setting to se-connections
        if len(connection_functions.values()) > 0:
            keys = connection_functions.keys()

            for connection in ConnectionsModel.query(apply_to):
                cfs = copy.deepcopy(connection_functions)
                functions = dict(
                    (str(item.function).strip().lower(), item)
                    for item in connection.functions
                    if item.function
                )

                for key in list(set(list(keys) + list(functions.keys()))):
                    if functions.get(str(key).strip().lower()):
                        cfs[str(key).strip().lower()] = functions[
                            str(key).strip().lower()
                        ]

                for k, v in cfs.items():
                    # v.aws_lambda_arn = aws_lambda_arn
                    cfs[k] = v

                for k, v in cfs.items():
                    if k == "sync_data":
                        print(k, ":::", v.setting, v.function, "\r\n")

                statements.append(
                    {
                        "statement": ConnectionsModel(
                            apply_to,
                            connection.api_key,
                            **{
                                "functions": cfs.values(),
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


def get_env_variables(settings, variable_name):
    if type(settings) is dict and settings.get(str(variable_name).strip()):
        return settings.get(str(variable_name).strip())

    load_dotenv()

    return os.getenv(
        key=str(variable_name).strip(),
        default=os.getenv(
            key=str(variable_name).strip().upper(),
            default=os.getenv(str(variable_name).strip().lower()),
        ),
    )
