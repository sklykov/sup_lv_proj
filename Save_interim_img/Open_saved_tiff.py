# -*- coding: utf-8 -*-
"""
Open the saved interim tiff file and measure performance.

@author: sklykov
"""
# %% Imports
from PIL import Image
import numpy as np
import time

# %% Tests
start = time.time()
img = Image.open("img.tif", mode='r')
img = np.array(img)
finish = time.time()
print("Operation takes:", round(1000*(finish - start), 1), "ms")
