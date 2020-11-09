# -*- coding: utf-8 -*-
"""
Test UDP server - open, receive, close by passing opening UDP server to multiprocessing.Process.

It doesn't work unfortunately because the server doesn't launches...

@author: ssklykov
"""
# %% Imports
import socket
import time
from multiprocessing import Process, Array
# import ctypes
# import numpy as np

# %% Parameters
host = 'localhost'
port_py_main = 5005  # number of the first ports of that will be opened
port_py = 5010  # number of the first ports of that will be opened
port_LV = 5100
st_n_bytes = 1024


# %% Methods to be used
def openIndependentPort(host, port_number, sharedString):
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    time.sleep(0.05)
    st_n_bytes = 1024
    sharedString.value = 'entered to a subprocess'
    try:
        sock.bind((host, port_number))
        (data, address) = sock.recvfrom(st_n_bytes)
        # data = str(data, encoding='utf-8')  #  decoding will be at another place
        sharedString.value = data
        sendingString = "port " + str(port_py) + " OPENED"
        sendingString = sendingString.encode()  # to utf-8
        sock.sendto(sendingString, address)
        time.sleep(0.3)
    finally:
        sock.close()


# %% Test independent UDP spawned servers - main part of a program
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

        elif "Open ports" in command:
            print(command, '- received command')
            sendingString = "ports" + " " + str(port_py) + " " + str(port_py+1) + " " + " will be opened"
            sendingString = sendingString.encode()  # to utf-8
            mainServer.sendto(sendingString, address)
            # receiver1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # receiver2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # String should be implemented in different way
            # recStr1 = Value(ctypes.c_wchar_p, 'empty')  # holder of a string
            # recStr2 = Value(ctypes.c_wchar_p, 'empty')
            recStr1 = Array('c', range(50))  # 50 chars for bytearray string
            recStr2 = Array('c', range(50))
            # sock1 = Process(target=openIndependentPort, args=(receiver1, host, port_py, recStr1))
            # sock2 = Process(target=openIndependentPort, args=(receiver2, host, port_py + 1, recStr2))
            sock1 = Process(target=openIndependentPort, args=(host, port_py, recStr1))
            sock2 = Process(target=openIndependentPort, args=(host, port_py + 1, recStr2))
            sock1.start()
            sock2.start()
            print("1st process id:", sock1.pid)
            print("2nd process id:", sock2.pid)
            sock1.join()
            sock2.join()
            time.sleep(4)
            print("Received from 1st socket:", recStr1.value.decode())
            print("Received from 2nd socket:", recStr2.value.decode())

        elif "QUIT" in command:
            print(command, '- received command')
            # Do the quiting action with a delay
            sendingString = "Quit performed".encode()
            mainServer.sendto(sendingString, address)
            time.sleep(0.15)  # A delay for preventing of closing connection automatically by Python (causing errors)
            flag = False
            break

    # time.sleep(1)
