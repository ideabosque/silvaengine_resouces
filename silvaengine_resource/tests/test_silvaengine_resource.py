#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bl"

import logging, sys, unittest, os
from silvaengine_utility import Utility
from dotenv import load_dotenv

load_dotenv()

setting = {
    "region_name": os.getenv("AWS_REGION_NAME"),
    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
}

sys.path.insert(0, "/var/www/projects/silvaengine_resouces")

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
                [
                    "analytics_engine",
                    "user_engine",
                    "shipping_quote_engine",
                    "seller_engine",
                    "factory_engine",
                ]
            )
        )

    # @unittest.skip("demonstrating skipping")
    def test_graphql_get_resource(self):

        variables = {
            "limit": 1000,
            "lastEvaluatedKey": {},
            # "resourceId": "5efb66cd78a2d3e22a545eca272871de",
        }
        query = """
            query resources($limit: Int!, $lastEvaluatedKey: JSON, $resourceId: String) {
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
