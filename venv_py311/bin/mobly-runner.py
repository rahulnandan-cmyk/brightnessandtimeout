#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import re
import sys

# This path should point to the correct function in the Mobly package
from mobly.test_runner import main

if __name__ == '__main__':
    # This block executes the Mobly runner function
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())