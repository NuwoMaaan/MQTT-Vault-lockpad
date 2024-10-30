import os
import socket
import re

host = 'www.google.com'
port = 80

def CreateSocket(path):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        
            request = f"GET {path} HTTP/1.0\r\nHost: {host}\r\n\r\n"
            print(request)
            s.send(request.encode())
            response = bytes()
            data = s.recv(8192)
            response += data
            if path == '/':
                html = response.decode()
            else:
                html = response
            return html
        except Exception:
            print("Connection Error: Couldn't Create socket")    

def parse_png(png):
    _, _, section_body = png.partition(b'\r\n\r\n')
    return section_body
        
def parse_html(html):
    section_header, _, section_body = html.partition('\r\n\r\n')
    status_line, _, _  = html.partition('\n')
    status_line = status_line.split()

    status_line_dict = {
            'Protocol': status_line[0],
            'Response Code': status_line[1],
            'Message': status_line[2]
        }
    
    return section_header, status_line_dict, section_body
    
def print_headers(section_header, status_line_dict):
    header_dict = {}

    if status_line_dict['Response Code'] == '200':
        for header in section_header.splitlines()[1:]:
            if ':' in header:
                key,value = header.split(':', 1)
                header_dict[key.strip()] = value.strip() 

        max_key_length = max(len(key) for key in header_dict)
        print(f"\nWebsite downloaded using {status_line_dict['Protocol']}\nHTTP response code: {status_line_dict['Response Code']} with message: {status_line_dict['Message']}")
        for key in header_dict:
            print(f"{key.ljust(max_key_length)} : {header_dict[key]}")
    else:
        raise Exception(f'Connection Error:{status_line_dict["Response Code"]}')

def Download_IMG(status_line_dict, section_body):
    #<meta content="/logos/doodles/2024/celebrating-popcorn-6753651837110076.2-l.png"
    #img_pattern = r'<meta content="/logos/doodles/2024/celebrating-popcorn-6753651837110076.2-l.png'
    pattern = r'<meta content="([^"]+)" itemprop="image">'
    if status_line_dict['Response Code'] == '200':
        for _img in re.findall(pattern, section_body):
            print(_img)
            filename = os.path.basename(_img)
            print(filename)

            ConstructAndDownload(filename, _img)

    else:
        raise Exception(f'Connection Error:{status_line_dict["Response Code"]}')


def ConstructAndDownload(filename, filepath):
     current_dir = os.getcwd() + f'\\{filename}'
     
     get_img = CreateSocket(filepath)
     png = parse_png(get_img)
     with open(current_dir, 'wb') as SaveImg:
        SaveImg.write(png)

############
def connect():
    try:
        html = CreateSocket('/')
        section_header, status_line_dict, section_body = parse_html(html)
        print_headers(section_header, status_line_dict)
        Download_IMG(status_line_dict, section_body)
        #print(section_body)
                        
    except Exception as error:
        print(f'Connection Error:{error}')

connect()

