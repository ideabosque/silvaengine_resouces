from pynamodb.expressions.condition import Condition
from .models import ResourceModel, FunctionsModel, ConfigDataModel, Status
from pynamodb.connection import Connection
from pynamodb.transactions import TransactWrite
from pynamodb.exceptions import TransactWriteError
from datetime import datetime
from importlib.util import find_spec
from importlib import import_module
from hashlib import md5
import uuid


def _add_resource_handler(packages):
    statements = []
    # Insert a resource record.
    updated_by = "setup"
    # Deploy area
    area = "core"
    endpoint_id = "1"
    # @TODO: If the current module which is installing shoud be attach some custom settting item, we need to support them.
    settings = {
        "region_name": ResourceModel.Meta.region,
        "area": area,
        "endpoint_id": endpoint_id,
        "aws_access_key_id": ResourceModel.Meta.aws_access_key_id,
        "aws_secret_access_key": ResourceModel.Meta.aws_secret_access_key,
    }

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
                factor = "{}-{}-{}-{}".format(
                    profile.get("service"),
                    package,
                    profile.get("class"),
                    function_name,
                )
                # TODO: Get region / IAM Number from env.
                aws_lambda_arn = "arn:aws:lambda:us-west-2:305624596524:function:silvaengine_microcore"
                resouce_id = md5(factor.encode(encoding="UTF-8")).hexdigest()
                # Add new resource to table
                statements.append(
                    {
                        "statement": ResourceModel(
                            resouce_id,
                            profile.get("service"),
                            **{
                                "module_name": package,
                                "class_name": profile.get("class"),
                                "function": function_name,
                                "label": config.get("label")
                                if config.get("label")
                                else "",
                                "status": Status.enabled,
                                "created_at": datetime.utcnow(),
                                "updated_at": datetime.utcnow(),
                                "updated_by": updated_by,
                            }
                        ),
                        # "condition": ResourceModel.resource_id != resouce_id,
                    }
                )

                # Add new function to table
                statements.append(
                    {
                        "statement": FunctionsModel(
                            aws_lambda_arn,
                            function_name,
                            **{
                                "area": area,
                                "config": {
                                    "class_name": profile.get("class"),
                                    "function_type": config.get("type")
                                    if config.get("type")
                                    else "RequestResponse",
                                    "methods": config.get("support_methods")
                                    if type(config.get("support_methods")) is list
                                    and len(config.get("support_methods"))
                                    else ["post", "get"],
                                    "module_name": package,
                                    "setting": config.get("settings")
                                    if config.get("settings")
                                    else "",
                                    "auth_required": bool(
                                        config.get("is_auth_required")
                                    )
                                    if config.get("is_auth_required")
                                    else False,
                                    "graphql": bool(config.get("is_graphql"))
                                    if config.get("is_graphql")
                                    else True,
                                    "operations": {
                                        "create": config.get("create")
                                        if type(config.get("create")) is list
                                        and len(config.get("create"))
                                        else [],
                                        "query": config.get("query")
                                        if type(config.get("query")) is list
                                        and len(config.get("query"))
                                        else [],
                                        "update": config.get("update")
                                        if type(config.get("update")) is list
                                        and len(config.get("update"))
                                        else [],
                                        "delete": config.get("delete")
                                        if type(config.get("delete")) is list
                                        and len(config.get("delete"))
                                        else [],
                                    },
                                },
                            }
                        ),
                        # "condition": FunctionsModel.function.does_not_exist(),
                    }
                )

        # Insert settings for module.
        for key, value in settings.items():
            statements.append(
                {
                    "statement": ConfigDataModel(
                        package,
                        key,
                        **{
                            "value": value,
                        }
                    )
                }
            )

    # Insert by batch
    # @TODO: If statements total more than 25, should use batchWrite to replace.
    with TransactWrite(
        connection=Connection(region=ResourceModel.Meta.region),
        client_request_token=uuid.uuid1().hex,
    ) as transaction:
        for item in statements:
            if item.get("condition"):
                transaction.save(
                    item.get("statement"), condition=(item.get("condition"))
                )
            else:
                transaction.save(item.get("statement"))
