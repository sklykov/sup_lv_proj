# -*- coding: utf-8 -*-
"""
Test of parcing of stdin - image coded in a string.
This script echoes some image data (mean or average pixel value).
This scrip is called by execute command in command line in a headless mode.

@author: ssklykov
"""
# %% Imports
import sys
# import time
import numpy as np

# %% Main testing
# data = sys.stdin.read()  # read all data until EOF
# print(data)  # return the read data to the standard output (could be accessed in the LV code in string form)
data = sys.stdin.readlines()

# Below - purely depends, sure, on the data sent from LV
if len(data) == 3:
    width = int(data[0])
    height = int(data[1])
    raw_img = data[2]
    raw_img = raw_img.split()  # split to numbers using standard whitespace as a separator
    # print("Image sizes [pixels]:", width, "x", height)  # for debugging
    img = np.zeros((height, width), dtype="uint16")  # image initialization (container)
    for i in range(height):
        img[i, :] = np.uint16(raw_img[i*width:(i+1)*width])
    # print(img)  # for debugging
    print("Image received")

    # # Simulation of some computation work
    # max_pixel = np.max(img)
    # print("Max image pixel:", max_pixel)
    average = np.mean(img)
    print("Average pixel value:", round(average))

else:
    print("Some data is corrupted")
