import socket
import re
import threading

HOST = '127.0.0.1' 
PORT = 4557 

ADDR = (HOST,PORT)

def CheckMessage(data,addr):
    pattern = r'^\(\d+\)TNE20003: [\x20-\x7E]+\n$'
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

def HandleClient(conn, addr):
    print(f'Connection with: {addr}')
    while True:
        data = conn.recv(1024)
        #d_data = f'({delineation}){data.decode()}{end_delineation}'
        if not data: 
                print(f'Connection closed: {addr}')
                break
        if CheckMessage(data.decode(),addr):
            print(f'Recieved data from: {addr}, DATA: {data.decode().strip()}')
            data = FormatA(data.decode())
            conn.send(data.encode())
            print(f'Echoing data: {data}')
        else:
            conn.send(error.encode())
            continue
    
    conn.close()

# --- Start multiple shells to see similar output here that shows unique start delineation for each shell and message---
# --- \n to indicate end of message, both start and end are checked in CheckMessage() after formatting is handled --- 
# Recieved data from: ('127.0.0.1', 57321), DATA: (1)TNE20003: hello
# Echoing data: TNE20003:A: hello
# Recieved data from: ('127.0.0.1', 57321), DATA: (2)TNE20003: leo holden
# Echoing data: TNE20003:A: leo holden
# Connection with: ('127.0.0.1', 57322)
# Waiting connection...
# Recieved data from: ('127.0.0.1', 57322), DATA: (1)TNE20003: new shell
# Echoing data: TNE20003:A: new shell
# Recieved data from: ('127.0.0.1', 57322), DATA: (2)TNE20003: hello with new shell
# Echoing data: TNE20003:A: hello with new shell
# Recieved data from: ('127.0.0.1', 57322), DATA: (3)TNE20003: hello again with new shell
# Echoing data: TNE20003:A: hello again with new shell
#MODIFIED TO HAVE CLIENT FORMAT MESSAGE WITH START AND END DELIN, THEN CHECKED AT SERVER (ZIP FILE HAS SERVER DELIN)        

def server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen(5)
    print('Serving listening...')
    
    while True:
        print('Waiting connection...')
        conn, addr = server.accept()
        thread = threading.Thread(target=HandleClient, args=(conn, addr))
        thread.start()
        
        

def main():
    server()
    
    

if __name__ == '__main__':
    try:
        main()
    except socket.error as err:
        print(f'Socket Library Error: {err}')

