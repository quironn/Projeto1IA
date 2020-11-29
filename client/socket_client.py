#!/usr/bin/env python3
import socket
import time
import ast

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 50001      # The port used by the server

def message(data):
    print("Data:",data)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        action, value = input("Insert action value pairs:").split()
        print("Action Value pair:", action, ":", value)
        s.sendall(str.encode(action+" "+value))
        data = s.recv(2048)
        print('Received', repr(data))
        msg = data.decode()
        #test
        print(msg)
        #message(ast.literal_eval(data.decode()))
        time.sleep(0.5)



