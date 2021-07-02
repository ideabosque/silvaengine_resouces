from silvaengine_utility import Utility
from .types import ResourceType, ResourcesType, LastEvaluatedKey
from .models import ResourceModel


def resolve_resources(info, **kwargs):
    limit = kwargs.get("limit")
    last_evaluated_key = kwargs.get("last_evaluated_key")
    resource_id = kwargs.get("resource_id")

    if resource_id is not None:
        resources = ResourceModel.query(resource_id, None)

        return [
            ResourceType(
                **Utility.json_loads(
                    Utility.json_dumps(resource.__dict__["attribute_values"])
                )
            )
            for resource in resources
        ]

    if last_evaluated_key is not None:
        results = ResourceModel.scan(
            limit=int(limit),
            last_evaluated_key=Utility.json_loads(last_evaluated_key),
        )
    else:
        results = ResourceModel.scan(limit=int(limit))

    resources = [resource for resource in results]
    # last_evaluated_key = results.last_evaluated_key

    return ResourcesType(
        items=[
            ResourceType(
                **Utility.json_loads(
                    Utility.json_dumps(dict(**resource.__dict__["attribute_values"]))
                )
            )
            for resource in resources
        ],
        last_evaluated_key=LastEvaluatedKey(
            hash_key=results.last_evaluated_key.get("resource_id").get("S"),
            range_key=results.last_evaluated_key.get("service").get("S"),
        ),
    )
