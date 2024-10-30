import socket
import os
import struct

host = "127.0.0.1"  
port = 4557  

param = (host, port)

def Connect():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(param)
        delin = 1
        while True:
            message, delin = GetMessage(delin)
            response = bytes()
            s.send(message.encode())
            data = s.recv(1024)
            response += data
            if not data:
                break
            print(response.decode())
          
            

def GetMessage(delin):
    end_delineation = '\n'
    header = 'TNE20003'
    print('Enter message: ')
    message = (f'({delin}){header}: {input()}{end_delineation}')
    delin += 1
    return message, delin

def main():
    Connect()
    
    


if __name__ == '__main__':
    try:
        main()
    except socket.error as err:
        print(f'Socket Library Error: {err}')





