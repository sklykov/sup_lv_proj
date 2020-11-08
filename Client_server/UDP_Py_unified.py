# -*- coding: utf-8 -*-
"""
Server implemented as the low-level python code here.

This script is called by the LabVIEW code for sending / receiving commands.
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


# %% Decoding numbers from a received string (through TCP connection)
def decodeNumbers(receivedStr: str) -> list:
    """Decode string containing numbers ('.' - as a decimal point) to a list containing numbers."""
    decodedList = []
    listStringNumbers = receivedStr.split(' ')  # Splitting received numbers to the list
    listStringNumbers.remove('')  # Removing the last empty character
    # print(listStringNumbers, ' - separated numbers')  # Debugging
    for numberStr in listStringNumbers:
        # print(numberStr, ' - single number in a string')  # Debugging
        number = float(numberStr)
        decodedList.append(number)
    return decodedList


# %% Decoding pixel values


# %% Encoding list of numbers into string for sending it (through TCP connection)
def encodeNumbers(numbersInList: list) -> str:
    """Encode list of numbers to a string for sending it to a client."""
    sending_string = str(numbersInList)
    # Make a pour string with numbers - below removing brackets and white spaces
    sending_string = sending_string.replace('[', '')
    sending_string = sending_string.replace(']', '')
    sending_string = sending_string.replace(',', '')
    sending_string = sending_string.encode()  # Default encdoing - utf-8
    return sending_string


# %% TCP communication with LabVIEW code
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
                n_rows_tr = 11000 // width
                n_chunks = height // n_rows_tr
                n_last_transfer = height - (n_chunks * n_rows_tr)
                if n_last_transfer > 0:
                    n_chunks += 1
                print("# of chunks:", n_chunks)
                print("# for last transfer:", n_last_transfer)
                # Below - receiving an image in chunks
                for i in range(n_chunks):
                    (raw_chunk, address) = s.recvfrom(img_max_size)
                    raw_chunk = (str(raw_chunk, encoding='utf-8'))
                    string_chunk = raw_chunk.split()  # using standard whitespace as a separator
                    # print("string chunk:", string_chunk)
                    if i < (n_chunks - 1):
                        for j in range(n_rows_tr):
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
