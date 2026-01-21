#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "bl"

import logging
import os
import sys
import unittest

from dotenv import load_dotenv

load_dotenv()

setting = {
    "region_name": os.getenv("AWS_REGION_NAME"),
    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
}

module_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
)
sys.path.append(module_path)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

from silvaengine_resource import Resource


class SilvaEngineResourceTest(unittest.TestCase):
    def setUp(self):
        self.resource = Resource(logger, **setting)
        logger.info("Initiate SilvaEngineResourceTest ...")

    def tearDown(self):
        logger.info("Destory SilvaEngineResourceTest ...")

    # @unittest.skip("demonstrating skipping")
    def test_add_resource(self):
        logger.info(
            self.resource.add_resource(
                "silvaengine_microcore_ewp",
                "ewp",
                "core",
                [
                    "analytics_engine",
                    "user_engine",
                    "shipping_quote_engine",
                    "seller_engine",
                    "factory_engine",
                ],
            )
        )

    # @unittest.skip("demonstrating skipping")
    def test_graphql_get_resource(self):
        variables = {
            "limit": 1000,
            "lastEvaluatedKey": {},
        }
        query = """
            query resources($limit: Int!, $lastEvaluatedKey: JSONCamelCase, $resourceId: String) {
                resources(limit: $limit, lastEvaluatedKey: $lastEvaluatedKey, resourceId: $resourceId) {
                    items {
                        resourceId
                        service
                        moduleName
                        className
                        function
                        label
                        status
                        createdAt
                        updatedAt
                        updatedBy
                        operations {
                            query {
                                label
                                action
                            }
                            mutation {
                                label
                                action
                            }
                        }
                    }
                    lastEvaluatedKey
                }
            }
        """

        payload = {"query": query, "variables": variables}
        response = self.resource.resource_graphql(**payload)
        logger.info(response)


if __name__ == "__main__":
    unittest.main()
