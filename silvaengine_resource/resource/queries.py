#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from silvaengine_utility import Utility
from .types import ResourceType, ResourcesType
from .models import ResourceModel

__author__ = "bl"


def resolve_resources(info, **kwargs):
    def get_value(results, key, data_type) -> str:
        if (
            results
            and key
            and data_type
            and results.get(key)
            and results.get(key).get(data_type)
        ):
            return results.get(key).get(data_type)

        return ""

    limit = kwargs.get("limit")
    last_evaluated_key = kwargs.get("last_evaluated_key")
    resource_id = kwargs.get("resource_id")

    if resource_id:
        resources = ResourceModel.query(resource_id, None)

        return [
            ResourceType(
                **Utility.json_loads(
                    Utility.json_dumps(resource.__dict__["attribute_values"])
                )
            )
            for resource in resources
        ]

    results = ResourceModel.scan(
        limit=int(limit), last_evaluated_key=last_evaluated_key
    )

    resources = [
        ResourceType(
            **Utility.json_loads(
                Utility.json_dumps(dict(**resource.__dict__["attribute_values"]))
            )
        )
        for resource in results
    ]

    if results.total_count < 1:
        return None

    return ResourcesType(
        items=resources,
        last_evaluated_key=Utility.json_loads(
            Utility.json_dumps(results.last_evaluated_key)
        ),
    )
