#/usr/bin/env/python3
"""Combined Display test - brightness and timeout"""

import sys
import  os

import logging

# Add the parent directory to Python path to find utils module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mobly import asserts