# -*- coding: utf-8 -*-

__title__ = "steam.ext.tf2"
__author__ = "Gobot1234"
__license__ = "MIT"
__version__ = "1.0.0a"

import vdf

from .client import *
from .protobufs.base_gcmessages import BluePrintResponse
from .backpack import *

VDF_DECODER = vdf.loads
VDF_ENCODER = vdf.dumps

del vdf
