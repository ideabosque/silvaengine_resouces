#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from enum import Enum

__author__ = "bl"


class Channel(Enum):
    SS3 = "ss3"
    EWP = "ewp"
    SOCIAL_NETWORK = "sn"


class SwitchStatus(Enum):
    YES = 1
    NO = 0
