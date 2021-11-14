from sys import version_info

if version_info.major != 3:
    # If python version not Python3
    raise ImportError("Module 'vk_bots' requires Python 3. Please update(or downdate) your Python to Python 3")

from .__main__ import VKBots
from .longpoll import LongPollManager
from .exceptions import *
from . import utils, types, enums

__version__ = "1.0.0"
__author__ = "RedHolms"