import vdf

from .backpack import *
from .client import *
from .currency import *
from .enums import *

VDF_DECODER = vdf.loads  #: The default VDF decoder to use
VDF_ENCODER = vdf.dumps  #: The default VDF encoder to use

del vdf
