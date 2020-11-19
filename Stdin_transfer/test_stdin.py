# -*- coding: utf-8 -*-
"""
Test of parcing of stdin.
This script echoes the stdin using standard print function.

@author: ssklykov
"""
# %% Imports
import sys
# import time

# %% Main testing
data = sys.stdin.read()  # read all data until EOF
print(data)  # return the read data to the standard output (could be accessed in the LV code in string form)
