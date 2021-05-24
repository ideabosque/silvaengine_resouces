#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "bibow"

from .handlers import _add_resource_handler


class Resource(object):
    def __init__(self, logger, **setting):
        self.logger = logger
        self.setting = setting

    @staticmethod
    def add_resource(packages):
        return _add_resource_handler(packages)
