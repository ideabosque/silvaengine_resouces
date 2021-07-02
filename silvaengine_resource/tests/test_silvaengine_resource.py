#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bl"

import logging, sys, unittest, os
from silvaengine_utility import Utility
from dotenv import load_dotenv

load_dotenv()

setting = {
    "region_name": os.getenv("region_name"),
    "aws_access_key_id": os.getenv("aws_access_key_id"),
    "aws_secret_access_key": os.getenv("aws_secret_access_key"),
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

    @unittest.skip("demonstrating skipping")
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
        # query = """
        #     query resources(
        #             $limit: Int!
        #         ){
        #         resources(
        #             limit: $limit
        #         ){
        #             resourceId
        #             service
        #             moduleName,
        #             className,
        #             function,
        #             operations,
        #             label,
        #             status
        #             createdAt
        #             updatedAt
        #             updatedBy
        #             lastEvaluatedKey
        #         }
        #     }
        # # """

        variables = {
            "limit": 1,
            "lastEvaluatedKey": {
                "hashKey": "053429072013b1fc6eeac9555cd4618b",
                "rangeKey": "subscription_management",
            },
        }

        query = """
            query resources($limit: Int!, $lastEvaluatedKey: PageInputType) {
                resources(limit: $limit, lastEvaluatedKey: $lastEvaluatedKey) {
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
                            create {
                                label
                                action
                            }
                            query {
                                label
                                action
                            }
                            update {
                                label
                                action
                            }
                            delete {
                                label
                                action
                            }
                        }
                    }
                    lastEvaluatedKey {
                        hashKey
                        rangeKey
                    }
                }
            }

        """

        # variables = {
        #     "limit": 1,
        #     "lastEvaluatedKey": Utility.json_dumps(
        #         {
        #             "service": {"S": "subscription_management"},
        #             "resource_id": {"S": "053429072013b1fc6eeac9555cd4618b"},
        #         }
        #     ),
        # }

        payload = {"query": query, "variables": variables}
        response = self.resource.resource_graphql(**payload)
        logger.info(response)


if __name__ == "__main__":
    unittest.main()
