# -*- coding: utf-8 -*-
"""
UDP server implemented as the low-level python code here.

This script is used in connection with the LabVIEW code for sending / receiving commands and, moreover,
images. This script is used for testing of capabilities of entire image transfer.
"""
# %% Imports
import socket
import time
import numpy as np

# %% Parameters (global)
host = 'localhost'
port = 5005  # Port for this script
port_listener = 5100
st_n_bytes = 1024


# %% Decoding pixel values - redundant explicit method

# %% Encoding list of numbers into string for sending it - RETAINED for needs of back communication
def encodeNumbers(numbersInList: list) -> str:
    """Encode list of numbers to a string for sending it to a client."""
    sending_string = str(numbersInList)
    # Make a pour string with numbers - below removing brackets and white spaces
    sending_string = sending_string.replace('[', '')
    sending_string = sending_string.replace(']', '')
    sending_string = sending_string.replace(',', '')
    sending_string = sending_string.encode()  # Default encdoing - utf-8
    return sending_string


# %% UDP communication with LabVIEW code for transferring an image
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((host, port))
    # Below - from TCP script
    # s.listen()
    # (connection, address) = s.accept()
    flag = True
    print("Python UDP Server launched")
    with s:
        while flag:
            (data, address) = s.recvfrom(st_n_bytes)  # Receive 1024 bytes of data from LV client (text commands)
            command = str(data, encoding='utf-8')  # Conversion to a normal string
            if "Ping" in command:
                print(command, '- received command')
                sendingString = "Echo"
                sendingString = sendingString.encode()  # to utf-8
                s.sendto(sendingString, address)

            if "Image" in command:
                print(command, '- received command')
                # sendingString = "Receiving an Image"
                # sendingString = sendingString.encode()  # to utf-8
                # s.sendto(sendingString, address)  # Confirmation to a client - not neccessary
                (width, address) = s.recvfrom(st_n_bytes)  # Height and width could be flipped!
                (height, address) = s.recvfrom(st_n_bytes)   # Height and width could be flipped!
                width = int(str(width, encoding='utf-8'))
                height = int(str(height, encoding='utf-8'))
                print("Sizes of an image [pixels]:", width, "x", height)  # debug
                img = np.zeros((height, width), dtype="uint16")  # image initialization (container)

                # (img_max_size, address) = s.recvfrom(st_n_bytes)  # estimation of image size in bytes
                # Really, after tests it was defined that maximum packet size for transfer through UDP in Windows
                # is about 8000 kb, so this number will be used as a constant to reduce transferring numbers

                img_max_size = 110*100*8  # ... bytes to be transferred ( ~ 80000 should be transferred w/t errors)
                # 11000 may seem as magical number but I haven't found the way to access it through some call
                # 11000 = 110 * 100 pixels that could be transferred w/t error through single UDP port (Win)
                n_rows_tr = 11000 // width
                n_chunks = height // n_rows_tr
                n_last_transfer = height - (n_chunks * n_rows_tr)
                if n_last_transfer > 0:
                    n_chunks += 1
                print("# of chunks:", n_chunks)
                print("# for last transfer:", n_last_transfer)
                print("# of rows for transfer", n_rows_tr)
                # s.settimeout(2)
                # Below - receiving an image in chunks
                for i in range(n_chunks):
                    (raw_chunk, address) = s.recvfrom(img_max_size)
                    raw_chunk = (str(raw_chunk, encoding='utf-8'))  # Converting byte string to normal one
                    string_chunk = raw_chunk.split()  # split to numbers using standard whitespace as a separator
                    # print("string chunk:", string_chunk)
                    if i < (n_chunks - 1):
                        for j in range(n_rows_tr):
                            # Transfer by a row to cumulative image
                            img[i*n_rows_tr + j, :] = np.uint16(string_chunk[width*j:width*(j+1)])
                    if (i == (n_chunks - 1)) and (n_last_transfer > 0):
                        for j in range(n_last_transfer):
                            img[i*n_rows_tr + j, :] = np.uint16(string_chunk[width*j:width*(j+1)])
                    elif (i == (n_chunks - 1)):
                        for j in range(n_rows_tr):
                            img[i*n_rows_tr + j, :] = np.uint16(string_chunk[width*j:width*(j+1)])
                print("Image receiving completed")
                sendingString = "An Image received"
                sendingString = sendingString.encode()  # to utf-8
                s.sendto(sendingString, address)

            elif "QUIT" in command:
                print(command, '- received command')
                # Do the quiting action with a delay
                s.sendto(sendingString, address)
                time.sleep(0.2)  # A delay for preventing of closing connection automatically by Python (causing errors)
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
