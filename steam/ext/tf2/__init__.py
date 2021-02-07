# -*- coding: utf-8 -*-

__title__ = "steam.ext.tf2"
__author__ = "Gobot1234"
__license__ = "MIT"
__version__ = "1.0.0"

import vdf

from .backpack import *
from .client import *
from .enums import *

VDF_DECODER = vdf.loads  #: The default VDF decoder to use
VDF_ENCODER = vdf.dumps  #: The default VDF encoder to use

del vdf
