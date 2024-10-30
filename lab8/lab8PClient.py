import socket
import os
import struct

host = "127.0.0.1"  
port = 4557  

param = (host, port)

def Connect():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        while True:
            message = GetMessage()
            response = bytes()
            s.sendto(message.encode(), param)
            data, addr = s.recvfrom(1024)
            response += data
            if not data:
                break
            print(response.decode())
          
            

def GetMessage():
    header = 'TNE20003'
    print('Enter message: ')
    message = (f'{header}: {input()}')
    return message

def main():
    Connect()
    
    


if __name__ == '__main__':
    try:
        main()
    except socket.error as err:
        print(f'Socket Library Error: {err}')





