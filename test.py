import ctypes
import threading
import time
import numpy as np
""" Python wrapper for the C shared library mylib"""
import sys
import platform
import ctypes
import ctypes.util

# Find the library and load it
import sys
n_bits = 32 << bool(sys.maxsize >> 32)
print(n_bits)
print("Unable to load the system C library")
