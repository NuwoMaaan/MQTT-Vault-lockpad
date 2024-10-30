
import socket
import requests
from bs4 import BeautifulSoup as BS
import os




HOST = "8.8.8.8"
PORT = 443



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))
    s.sendall(bytes("hello","utf-8"))      #s.sendall(b"hello")
    data = s.recv(1024)



URL = "http://www.google.com/"



def DownloadHTML(request):
    html_response = request.text
    return html_response

def DownloadIMG(request):
    findIMG = BS(request, 'html.parser')
    for _img in findIMG.find_all('img'):
        print("\n")
        print(_img)
        print(_img['src'])
        filename = os.path.basename(_img['src'])
        print(filename)

        ContrustAndDownload(filename, _img['src'])

    return filename

def ContrustAndDownload(filename, filepath):

    construct_url = f'http://www.google.com.au{filepath}'
    r = requests.get(construct_url)
    current_dir = os.getcwd() + f'\\{filename}'
    with open(current_dir, 'wb') as SaveImg:
        SaveImg.write(r.content)
   

try:
    r = requests.get(URL)
   
    htmlText = DownloadHTML(r)
    filename = DownloadIMG(htmlText)


    metadata = r.headers 

    metadata_dict = dict(
        date = metadata.get("Date"),
        expires = metadata.get("Expires"),
        cache_control = metadata.get("Cache-Control"),
        content_type = metadata.get("Content-Type"),
        content_security_policy_report_only = metadata.get("Content-Security-Policy-Report-Only"),
        p3p = metadata.get("P3P"),
        content_encoding = metadata.get("Content-Encoding"),
        server = metadata.get("Server"),
        content_length = metadata.get("Content-Length"),
        x_xss_protection = metadata.get("X-XSS-Protection"),
        x_frame_options = metadata.get("X-Frame-Options"),
        set_cockie = metadata.get("Set-Cockie")
        )
    
    max_key_length = max(len(key) for key in metadata_dict)
    print(f"\n\n\nHTTP Response code {r.status_code} with message: OK")
    for key in metadata_dict:
        print(f"{key.ljust(max_key_length)} : {metadata_dict[key]}")

    
except Exception:
    print("Connection Error: Couldn't Connect")
    



    
    


   
    


    

