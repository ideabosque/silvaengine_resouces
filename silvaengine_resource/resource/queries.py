#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from silvaengine_utility import Utility
from .types import ResourceType, ResourcesType
from .models import ResourceModel

__author__ = "bl"


def resolve_resources(info, **kwargs):
    limit = kwargs.get("limit")
    last_evaluated_key = kwargs.get("last_evaluated_key")
    resource_id = kwargs.get("resource_id")
    filter_invisibles = lambda resource: resource.visible != False
    resources = []

    if resource_id:
        results = ResourceModel.query(str(resource_id).strip(), None)

        for resource in results:
            if str(resource.resource_id).strip() == str(resource_id).strip():
                resource.operations.query = list(
                    filter(filter_invisibles, resource.operations.query)
                )
                resource.operations.mutation = list(
                    filter(filter_invisibles, resource.operations.mutation)
                )

                if (
                    len(resource.operations.query) + len(resource.operations.mutation)
                    > 0
                ):
                    resources.append(
                        ResourceType(
                            **Utility.json_loads(
                                Utility.json_dumps(
                                    resource.__dict__["attribute_values"]
                                )
                            )
                        )
                    )

    else:
        results = ResourceModel.apply_to_resource_id_index.query(
            limit=int(limit),
            hash_key=str(info.context.get("channel")).strip(),
            last_evaluated_key=last_evaluated_key,
        )

        for resource in results:
            resource.operations.query = list(
                filter(filter_invisibles, resource.operations.query)
            )
            resource.operations.mutation = list(
                filter(filter_invisibles, resource.operations.mutation)
            )

            if len(resource.operations.query) + len(resource.operations.mutation) > 0:
                resources.append(
                    ResourceType(
                        **Utility.json_loads(
                            Utility.json_dumps(
                                dict(**resource.__dict__["attribute_values"])
                            )
                        )
                    )
                )

    if results.total_count < 1:
        return None

    return ResourcesType(
        items=resources,
        last_evaluated_key=Utility.json_loads(
            Utility.json_dumps(results.last_evaluated_key)
        ),
    )
