# -*- coding: utf-8 -*-
"""
Test capabilties of image transfer through saving it to the disk, reading and subsequent deleting.

@author: sklykov
"""
# %% Imports
from PIL import Image
import numpy as np
import time
import socket

# %% Script-wide parameters
host = 'localhost'
port_py_main = 5005  # number of the first ports of that will be opened
port_LV = 5100
st_n_bytes = 1024

# %% UDP server as listener for LabVIEW commands
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as mainServer:
    mainServer.bind((host, port_py_main))
    flag = True
    print("Python UDP Server launched")

    # Attempt to fix non-receiving commands for launching in an independent window
    # mainServer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # mainServer.setblocking(True)
    # mainServer.settimeout(1)
    # print(mainServer)

    while flag:
        (command, address) = mainServer.recvfrom(st_n_bytes)
        command = str(command, encoding='utf-8')  # Conversion to a normal string

        # if len(command) > 0:
        #     print(command)

        if "Ping" in command:
            print(command, '- received command')
            sendingString = "Echo"
            sendingString = sendingString.encode()  # to utf-8
            mainServer.sendto(sendingString, address)

        elif "Image saved" in command:
            print(command, '- received command')
            img = Image.open("img.tif", mode='r')
            img = np.array(img)
            print("Image readed and stored in this script")
            sendingString = "Image transferred".encode()
            mainServer.sendto(sendingString, address)
            # For simple check that some image transferred - perform some operation on an image
            print("Mean pixel value:", round(np.mean(img)))

        elif "QUIT" in command:
            print(command, '- received command')
            # Do the quiting action with a delay
            sendingString = "Quit performed".encode()
            mainServer.sendto(sendingString, address)
            time.sleep(0.15)  # A delay for preventing of closing connection automatically by Python (causing errors)
            flag = False
            break


# %% For correctly representation of an image - it should be performed after quiting of image transfer
# For testing if the transfer of an image perfromed correctly
try:
    if np.size(img, axis=0) > 0:
        from skimage import io
        from skimage.util import img_as_ubyte
        import matplotlib.pyplot as plt
        if np.max(img) < 256:
            img = np.uint8(img)
        img_show = img_as_ubyte(img)
        plt.figure("Transferred image")
        io.imshow(img_show)
except NameError:
    print("No image transferred")
