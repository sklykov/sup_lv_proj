# -*- coding: utf-8 -*-
"""
Test UDP server - open, receive, close.

@author: ssklykov
"""
# %% Imports
import socket
import time
# import numpy as np

# %% Parameters
host = 'localhost'
port_py_main = 5005  # number of the first ports of that will be opened
port_py = 5010  # number of the first ports of that will be opened
port_LV = 5100
st_n_bytes = 1024

# %% Test independent transfer - mainServer is opened below by "with" operator
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as mainServer:
    mainServer.bind((host, port_py_main))
    flag = True
    print("Python UDP Server launched")

    while flag:
        (command, address) = mainServer.recvfrom(st_n_bytes)
        command = str(command, encoding='utf-8')  # Conversion to a normal string
        if "Ping" in command:
            print(command, '- received command')
            sendingString = "Echo"
            sendingString = sendingString.encode()  # to utf-8
            mainServer.sendto(sendingString, address)

        elif "Open port" in command:
            print(command, '- received command')
            sendingString = "port " + str(port_py) + " will be opened"
            sendingString = sendingString.encode()  # to utf-8
            mainServer.sendto(sendingString, address)
            receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                receiver.bind((host, port_py))
                (data, address) = receiver.recvfrom(st_n_bytes)
                # print("from:", address)
                data = str(data, encoding='utf-8')
                print("Received:", data)
                sendingString = "port " + str(port_py) + " OPENED"
                sendingString = sendingString.encode()  # to utf-8
                receiver.sendto(sendingString, address)
                time.sleep(0.05)
            finally:
                receiver.close()

        elif "QUIT" in command:
            print(command, '- received command')
            # Do the quiting action with a delay
            mainServer.sendto(sendingString, address)
            time.sleep(0.15)  # A delay for preventing of closing connection automatically by Python (causing errors)
            flag = False
            break

    # time.sleep(1)
