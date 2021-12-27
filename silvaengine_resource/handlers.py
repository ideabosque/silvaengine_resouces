from .models import (
    ResourceModel,
    FunctionsModel,
    ConfigDataModel,
    ConnectionsModel,
    Status,
)
from silvaengine_utility import Utility
from pynamodb.connection import Connection
from pynamodb.transactions import TransactWrite
from pynamodb.exceptions import TransactWriteError
from datetime import datetime
from importlib.util import find_spec
from importlib import import_module
from hashlib import md5
import boto3

# import uuid


def _add_resource_handler(packages):
    identity = boto3.client(
        "sts",
        region_name=ResourceModel.Meta.region,
        aws_access_key_id=ResourceModel.Meta.aws_access_key_id,
        aws_secret_access_key=ResourceModel.Meta.aws_secret_access_key,
    ).get_caller_identity()

    if identity.get("Account") is None:
        return

    statements = []
    # Insert a resource record.
    # updated_by = "setup"
    # Deploy area
    area = ResourceModel.Meta.aws_api_area
    endpoint_id = ResourceModel.Meta.aws_endpoint_id
    # @TODO: If the current module which is installing shoud be attach some custom settting item, we need to support them.
    # settings = {
    #     "region_name": ResourceModel.Meta.region,
    #     "area": area,
    #     "endpoint_id": endpoint_id,
    #     "aws_access_key_id": ResourceModel.Meta.aws_access_key_id,
    #     "aws_secret_access_key": ResourceModel.Meta.aws_secret_access_key,
    # }
    # TODO: Get region / IAM Number from env.
    aws_lambda_arn = "arn:aws:lambda:{}:{}:function:silvaengine_microcore".format(
        ResourceModel.Meta.region, identity.get("Account")
    )
    now = datetime.utcnow()

    def getOperations(payload, returnMap=False) -> list:
        operations = []

        if payload is not None:
            attributes = ["label", "action"] if returnMap else ["action"]
            al = len(attributes)

            for item in payload:
                if al == 1:
                    for k in item.keys():
                        if k in attributes:
                            operations.append(item[k])
                else:
                    pairs = {}

                    for k in item.keys():
                        if k in attributes:
                            pairs[k] = item[k]

                    if len(pairs.keys()) == al:
                        operations.append(pairs)

        return operations

    # Insert resource / function / config data.
    for package in packages:
        # 1. Load module by dynamic
        spec = find_spec(package)

        if spec is None:
            continue

        module = import_module(package)

        if not hasattr(module, "deploy"):
            continue

        profiles = getattr(module, "deploy")()

        if type(profiles) is not list or len(profiles) < 1:
            continue

        # 2. Insert resource / function.
        for profile in profiles:
            if not profile.get("class"):
                continue

            for function_name, config in profile.get("functions").items():
                function_name = function_name.lower().strip()
                # Factor of generate resource ID
                factor = "{}-{}-{}".format(
                    package.strip(),
                    profile.get("class").strip(),
                    function_name,
                ).lower()
                resource_id = md5(factor.encode(encoding="UTF-8")).hexdigest()
                mutations = getOperations(config.get("create"), True)
                mutations += getOperations(config.get("update"), True)
                mutations += getOperations(config.get("delete"), True)

                try:
                    ResourceModel(resource_id, profile.get("service")).delete()
                except:
                    pass

                # Add new resource to table se-resource
                if not config.get("disabled_in_resources", False):
                    statements.append(
                        {
                            "statement": ResourceModel(
                                resource_id,
                                profile.get("service"),
                                **{
                                    "module_name": package,
                                    "class_name": profile.get("class"),
                                    "function": function_name,
                                    "label": config.get("label")
                                    if config.get("label")
                                    else "",
                                    "status": Status.enabled,
                                    "operations": {
                                        "mutation": mutations,
                                        # "create": getOperations(config.get("create"), True),
                                        "query": getOperations(
                                            config.get("query"), True
                                        ),
                                        # "update": getOperations(config.get("update"), True),
                                        # "delete": getOperations(config.get("delete"), True),
                                    },
                                    "created_at": now,
                                    "updated_at": now,
                                    # "updated_by": updated_by,
                                },
                            ),
                            # "condition": ResourceModel.resource_id != resource_id,
                        }
                    )

                # Add new function to table se-functions
                mutations = getOperations(config.get("create"))
                mutations += getOperations(config.get("update"))
                mutations += getOperations(config.get("delete"))
                statements.append(
                    {
                        "statement": FunctionsModel(
                            aws_lambda_arn,
                            function_name,
                            **{
                                "area": area,
                                "config": {
                                    "class_name": profile.get("class"),
                                    "funct_type": config.get("type")
                                    if config.get("type")
                                    else "RequestResponse",
                                    "methods": config.get("support_methods")
                                    if type(config.get("support_methods")) is list
                                    and len(config.get("support_methods"))
                                    else ["POST", "GET"],
                                    "module_name": package,
                                    "setting": config.get("settings")
                                    if config.get("settings")
                                    else package,
                                    "auth_required": bool(
                                        config.get("is_auth_required")
                                    )
                                    if config.get("is_auth_required")
                                    else False,
                                    "graphql": bool(config.get("is_graphql"))
                                    if config.get("is_graphql")
                                    else False,
                                    "operations": {
                                        # "create": getOperations(config.get("create")),
                                        "mutation": list(set(mutations)),
                                        "query": getOperations(config.get("query")),
                                        # "update": getOperations(config.get("update")),
                                        # "delete": getOperations(config.get("delete")),
                                    },
                                },
                            },
                        ),
                        # "condition": FunctionsModel.function.does_not_exist(),
                    }
                )

                # @TODO: Add function setting to se-connections

        # Insert settings for module.
        # for key, value in settings.items():
        #     statements.append(
        #         {
        #             "statement": ConfigDataModel(
        #                 package,
        #                 key,
        #                 **{
        #                     "value": value,
        #                 }
        #             )
        #         }
        #     )

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

    print("Done")
