#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

import logging, sys, json, unittest, uuid, os
from datetime import datetime, timedelta, date
from decimal import Decimal
from pathlib import Path
from silvaengine_utility import Utility

from dotenv import load_dotenv

load_dotenv()
setting = {
    "region_name": os.getenv("region_name"),
    "aws_access_key_id": os.getenv("aws_access_key_id"),
    "aws_secret_access_key": os.getenv("aws_secret_access_key"),
}

sys.path.insert(0, "/var/www/projects/silvaengine_resource")

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
        
        logger.info(self.resource.add_resource("silvaengine"))


if __name__ == "__main__":
    unittest.main()
