# -*- coding: utf-8 -*-
"""
Server implemented as low-level python code here.

This script is called by LabVIEW code.
"""
# %% Imports
import socket
import time

# %% Parameters (global)
host = 'localhost'
port = 8089


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
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    flag = True
    coordinates = []
    positions = []
    print("Python Server launched")
    (connection, address) = s.accept()
    print('Connected by', address)  # Debugging
    with connection:
        while flag:
            data = connection.recv(1024)  # Receive 1024 bytes of data (the buffer exceeded)
            command = str(data, encoding='utf-8')  # Conversion to a normal string
            if "Ping" in command:
                print(command, '- received command')
                sendingString = "Echo"
                sendingString = sendingString.encode()  # to utf-8
                connection.send(sendingString)

            elif "QUIT" in command:
                print(command, '- received command')
                # Do the quiting action with a delay
                connection.send(b'QUIT-DONE')
                time.sleep(0.2)  # A delay for preventing of closing connection automatically by Python
                flag = False
                break
