import socket
import re
from pynput.keyboard import Key, Listener
import struct

HOST = '127.0.0.1' 
PORT = 4557 

ADDR = (HOST,PORT)

def CheckMessage(data,addr):
    pattern = r'^TNE20003: [\x20-\x7E]+$'
    if re.match(pattern, data):
        return True
    else:
        global error
        error = f'TNE20003:E: FORMAT ERROR'
        print(f'Message from {addr} - incorrect format')
        return False

def FormatA(data):
    message = data.split(': ', 1)[1]
    data = f'TNE20003:A: {message}'
    return data

def server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(ADDR)
    
    while True:
        print('Waiting connection...')
        data, addr = server.recvfrom(1024)
        if CheckMessage(data.decode(),addr):
            print(f'Recieved data from: {addr}, DATA: {data.decode()}')
            if not data: 
                break
            data = FormatA(data.decode())
            server.sendto(data.encode(), addr)
            print(f'Echoing data: {data}')
        else:
            server.sendto(error.encode(), addr)
            continue
        
        

def main():
    server()
    

if __name__ == '__main__':
    try:
        main()
    except socket.error as err:
        print(f'Socket Library Error: {err}')

