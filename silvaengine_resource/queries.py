from silvaengine_utility import Utility
from .types import ResourceType, ResourcesType, LastEvaluatedKey
from .models import ResourceModel


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
    hash_key_field_name = ResourceModel._hash_keyname
    range_key_field_name = ResourceModel._range_keyname
    hash_key_field_data_type = (
        ResourceModel._hash_key_attribute().attr_type[0].upper()
        if ResourceModel._hash_key_attribute()
        else None
    )
    range_key_field_data_type = (
        ResourceModel._range_key_attribute().attr_type[0].upper()
        if ResourceModel._range_key_attribute()
        else None
    )

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

    if last_evaluated_key:
        values = {}

        for k, v in last_evaluated_key.items():
            key = k.lower()

            if key == "hash_key" and hash_key_field_name and hash_key_field_data_type:
                values[hash_key_field_name] = {hash_key_field_data_type: v}
            elif (
                key == "range_key"
                and range_key_field_name
                and range_key_field_data_type
            ):
                values[range_key_field_name] = {range_key_field_data_type: v}

        results = ResourceModel.scan(
            limit=int(limit),
            last_evaluated_key=values,
        )
    else:
        results = ResourceModel.scan(limit=int(limit))

    resources = [resource for resource in results]

    if results.total_count < 1:
        return None

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
            hash_key=get_value(
                results.last_evaluated_key,
                hash_key_field_name,
                hash_key_field_data_type,
            ),
            range_key=get_value(
                results.last_evaluated_key,
                range_key_field_name,
                range_key_field_data_type,
            ),
        ),
    )
