# -*- coding: utf-8 -*-
"""
Test UDP server - open, receive, close by passing opening UDP server to multiprocessing.Process.

It doesn't work unfortunately because the server doesn't launches...

@author: ssklykov
"""
# %% Imports
import socket
import time
from threading import Thread
# import numpy as np

# %% Parameters
host = 'localhost'
port_py_main = 5005  # number of the first ports of that will be opened
port_py = 5010  # number of the first ports of that will be opened
port_LV = 5100
st_n_bytes = 1024


# %% Independent UDP server as a thread
class independenPort(Thread):
    host = ''
    portN = 0
    sock = None

    def __init__(self, host, port_number):
        self.host = host
        self.portN = port_number
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        Thread.__init__(self)
        # print("Port", self.portN, "initialized")  # for debugging
        # print(self.sock, "- check socket object created")  # for debugging

    def run(self):
        # print("Attempt to initialize port", self.portN)  # for debugging
        sock = self.sock
        try:
            sock.bind((self.host, self.portN))
            sock.settimeout(2)
            print("Port", self.portN, "opened")
            (data, address) = sock.recvfrom(st_n_bytes)
            data = str(data, encoding='utf-8')  # decoding received data
            print("Received:", data)
            time.sleep(0.1)
            sendingString = "port " + str(self.portN) + " OPENED"
            sendingString = sendingString.encode()  # to utf-8
            sock.sendto(sendingString, address)
            time.sleep(0.4)
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
            port1 = independenPort(host, port_py)
            port2 = independenPort(host, port_py + 1)
            port1.start()
            port2.start()
            port1.join()
            port2.join()
            print("Open ports finished")

        elif "QUIT" in command:
            print(command, '- received command')
            # Do the quiting action with a delay
            sendingString = "Quit performed".encode()
            mainServer.sendto(sendingString, address)
            time.sleep(0.15)  # A delay for preventing of closing connection automatically by Python (causing errors)
            flag = False
            break
