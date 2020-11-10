# -*- coding: utf-8 -*-
"""
Test transfer of an image through threaded multiple UDP ports launched by this script and LV code.

This script should reveal performance and capability to send an image through two independent ports.

@author: ssklykov
"""
# %% Imports
import socket
import time
from threading import Thread
import numpy as np

# %% Parameters
host = 'localhost'
port_py_main = 5005  # number of the first ports of that will be opened
port_py = 5010  # number of the first ports of that will be opened
port_LV = 5100
st_n_bytes = 1024


# %% Independent UDP server as a thread
class independentImgPort(Thread):
    """
    Implement socket on individual thread launched by this class (subclass of Thread class with overriden
                                                                  methods __init__ and run).
    """
    host = ''
    portN = 0
    sock = None
    received_str = ''
    received_img_chunk = []

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
            time.sleep(0.1)
            # print("Port", self.portN, "opened")  # for debugging
            (data, address) = sock.recvfrom(st_n_bytes)
            data = str(data, encoding='utf-8')  # decoding received data
            print("Received:", data)
            self.received_str = data
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

        elif "Img multiports" in command:
            print(command, '- received command')
            # sendingString = "ports" + " " + str(port_py) + " " + str(port_py+1) + " " + " will be opened"
            # sendingString = sendingString.encode()  # to utf-8
            # mainServer.sendto(sendingString, address)
            # Code for image transfer has been taken from UDP_Py_unified module!!!
            (width, address) = mainServer.recvfrom(st_n_bytes)  # Height and width could be flipped!
            (height, address) = mainServer.recvfrom(st_n_bytes)  # Height and width could be flipped!
            width = int(str(width, encoding='utf-8'))
            height = int(str(height, encoding='utf-8'))
            print("Sizes of an image [pixels]:", width, "x", height)  # debug
            img = np.zeros((height, width), dtype="uint16")  # image initialization (container)
            img_max_size = 110*100*8
            n_rows_tr = 11000 // width
            n_chunks = height // n_rows_tr
            n_last_transfer = height - (n_chunks * n_rows_tr)
            if n_last_transfer > 0:
                n_chunks += 1
            print("# of chunks:", n_chunks)
            print("# for last transfer:", n_last_transfer)

            # port1 = independentImgPort(host, port_py)  # initialize 1st port
            # port2 = independentImgPort(host, port_py + 1)
            # port1.start()  # start listening to chunks to be transferred
            # port2.start()
            # port1.join()  # force this script to wait completion of data transfer
            # port2.join()
            # print("Collected data from ports:", port1.received_str, port2.received_str)
            print("Image transfer through multiports finished")
            sendingString = "Image transferred".encode()
            mainServer.sendto(sendingString, address)

        elif "QUIT" in command:
            print(command, '- received command')
            # Do the quiting action with a delay
            sendingString = "Quit performed".encode()
            mainServer.sendto(sendingString, address)
            time.sleep(0.15)  # A delay for preventing of closing connection automatically by Python (causing errors)
            flag = False
            break
