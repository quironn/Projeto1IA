#!/usr/bin/env python3
import socket
import time

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 50001      # The port used by the server


class Client:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.s = None

    def print_message(self, data):
        print("Data:", data)

    def connect(self):
        # try:
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))
#            return(0)
#        except:
#            print('A connection error occurred!')
#            return(-1)

    def execute(self, action, value, sleep_t=0.1):
        self.s.sendall(str.encode(action+" "+value))
        data = self.s.recv(2048)
        print('Received', repr(data))
        message = data.decode()
        # message(ast.literal_eval(data.decode()))
        time.sleep(sleep_t)
        return message


def main():
    client = Client(HOST, PORT)
    res = client.connect()
    if res != -1:
        while True:
            command = input("Insert action value pairs:").split()
            if len(command) != 2:
                action, value = "", ""
            else:
                action, value = command
            print("Action Value pair:", action, ":", value)
            msg = client.execute(action, value)
            # test
            client.print_message(msg)


if __name__ == "__main__":
    main()
