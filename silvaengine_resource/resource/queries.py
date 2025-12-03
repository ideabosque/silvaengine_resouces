#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import List, Dict, Any, Optional
from silvaengine_utility import Utility
from .types import ResourceType, ResourcesType
from .models import ResourceModel

__author__ = "bl"


def resolve_resources(info, **kwargs: Dict[str, Any]) -> Optional[ResourcesType]:
    limit = kwargs.get("limit")
    last_evaluated_key = kwargs.get("last_evaluated_key")
    resource_id = kwargs.get("resource_id")
    filter_invisibles = lambda resource: resource.visible != False
    resources: List[ResourceType] = []

    if resource_id:
        # Query by resource_id directly, no need to check again in loop
        resource_id_str = str(resource_id).strip()
        results = ResourceModel.query(resource_id_str, None)

        for resource in results:
            # Filter invisible operations
            visible_queries = [op for op in resource.operations.query if op.visible != False]
            visible_mutations = [op for op in resource.operations.mutation if op.visible != False]

            if len(visible_queries) + len(visible_mutations) > 0:
                # Directly use attribute_values without double json conversion
                resource_data = resource.__dict__["attribute_values"]
                # Update with filtered operations
                resource_data["operations"].query = visible_queries
                resource_data["operations"].mutation = visible_mutations
                
                resources.append(ResourceType(**resource_data))

    else:
        channel = info.context.get("channel")
        results = ResourceModel.scan(
            limit=int(limit) if limit else 100,
            filter_condition=(ResourceModel.apply_to == channel),
            last_evaluated_key=last_evaluated_key,
        )

        for resource in results:
            # Filter invisible operations
            visible_queries = [op for op in resource.operations.query if op.visible != False]
            visible_mutations = [op for op in resource.operations.mutation if op.visible != False]

            if len(visible_queries) + len(visible_mutations) > 0:
                # Directly use attribute_values without double json conversion
                resource_data = resource.__dict__["attribute_values"]
                # Update with filtered operations
                resource_data["operations"].query = visible_queries
                resource_data["operations"].mutation = visible_mutations
                
                resources.append(ResourceType(**resource_data))

    if not resources:
        return None

    # Only serialize last_evaluated_key if it exists
    last_key = None
    if hasattr(results, 'last_evaluated_key') and results.last_evaluated_key:
        last_key = results.last_evaluated_key

    return ResourcesType(
        items=resources,
        last_evaluated_key=last_key,
    )
