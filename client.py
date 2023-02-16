import socket
import os
from urllib.parse import urlparse
from pathlib import Path
import threading
from bs4 import BeautifulSoup

CTL_test1 = "http://example.com/" 
CTL_test2 = "http://example.com/index.html"
CTL_test3 = "http://web.stanford.edu/dept/its/support/techtraining/techbriefing-media/Intro_Net_91407.ppt"
CTL_test4 = "http://web.stanford.edu/class/cs224w/slides/01-intro.pdf"
CTL_test5 = "http://web.stanford.edu/class/cs224w/slides/08-GNN-application.pdf"
CTL_test6 = "http://web.stanford.edu/class/cs231a/assignments.html"
CTL_test7 = "http://web.stanford.edu/class/cs231a/project.html"

CHUNK_test1 = "http://www.google.com" 
CHUNK_test2 = "http://www.google.com/index.html"
CHUNK_test3 = "http://www.bing.com"
CHUNK_test4 = "http://anglesharp.azurewebsites.net/Chunked"
CHUNK_test5 = "http://www.httpwatch.com/httpgallery/chunked/chunkedimage.aspx"

SAVING_FOLDER1 = "http://web.stanford.edu/class/cs224w/slides/"
SAVING_FOLDER2 = "http://web.stanford.edu/class/cs142/lectures/"
SAVING_FOLDER3 = "http://web.stanford.edu/class/cs143/handouts/"
SAVING_FOLDER4 = "http://web.stanford.edu/class/cs231a/course_notes/"

FORMAT_WORD = 'utf-8'
OTHER_FORMAT = 'ISO-8859-1'
SUCCESSFUL_CONNECT_MESSAGE = 'Successfully established connection\n'
DISCONNECT_MESSAGE = 'Disconnected\n'
SUCCESSFUL_DOWNLOAD_MESSAGE = 'Successfully downloaded file\n'


def send_Request():
    request = 'GET /' + dir + ' HTTP/1.1\r\nHost:' + HOST + '\r\nAccept: text/html,image/gif,image/jpeg,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,audio/mpeg,video/mp4,application/pdf,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation,text/plain\r\nAccept-Language: en-US,en-GB\r\nConnection: keep-alive\r\n\r\n'
    client.sendall(request.encode(FORMAT_WORD))


def get_Header(data):
    while (not data.endswith(b'\r\n\r\n')):
        data += client.recv(1)
    return data


def Check_Response_Type():
    global isContent_Length
    global isChunked
    global header
    header = get_Header(header)
    tmpheader = str(header)
    
    if (tmpheader.find('Content-Length: ') != -1):
        isContent_Length = True
        isChunked = False
    elif (tmpheader.find('Transfer-Encoding: chunked') != -1):
        isContent_Length = False
        isChunked = True

def get_Content_Length(header) -> int:
    global format
    data = ''
    if (eof == 'ppt' or eof == 'pdf'):
        format = OTHER_FORMAT
    else:
        format = FORMAT_WORD
    data += str(header.decode(format))
    data = data.split('Content-Length: ', 1)[1]
    data = data.split('\r\n', 1)[0]
    return int(data)


def download_Content_Length():
    data = b'' #bytes
    CTlen = get_Content_Length(header)
    data += header
    while (len(data) < CTlen + len(header)):
        response = client.recv(1024)
        data += response
        if (not response):
            break
    client.close()
    
    content = data.split(b'\r\n\r\n', 1)[1]
    if (dir == '/' or dir == ''):
        with open('index.html', 'wb+') as file: 
            file.write(content)
            print(SUCCESSFUL_DOWNLOAD_MESSAGE)
            file.close()
    elif (eof == '.html'):
        with open(fname, 'wb+') as file:
            file.write(content)
            print(SUCCESSFUL_DOWNLOAD_MESSAGE)
            file.close()
    elif (eof == '.ppt'):
        with open(fname, 'wb+') as file:
            file.write(content)
            print(SUCCESSFUL_DOWNLOAD_MESSAGE)
            file.close()
    elif (eof == '.pdf'):
        with open(fname, 'wb+') as file:
            file.write(content)
            print(SUCCESSFUL_DOWNLOAD_MESSAGE)
            file.close()
      

def download_Chunked():
    data = b'' #final data
    
    flag = True
    while (flag):
        Reader = b''
        while (not Reader.endswith(b'\r\n')):
            Reader += client.recv(1)
        
        Reader = Reader[:-2]  #seperating '\r\n'
        Reader = int(Reader.decode(),16)
            
        tempData = b''
        chunked_data = b''
        
        chunked_data = client.recv(Reader)
        tempData += chunked_data
        
        chunked_len = len(chunked_data)
        
        while (chunked_len < Reader):
            chunked_data = client.recv(Reader - chunked_len)
            tempData += chunked_data
            chunked_len += len(chunked_data)
        client.recv(2)
        
        if (not Reader):
            flag = False
        data += tempData
    
    client.close()
    if (dir == '' or dir == '/'):
        with open('index.html', 'wb+') as file: 
            file.write(data)
            print(SUCCESSFUL_DOWNLOAD_MESSAGE)
            file.close()
    else:
        with open(fname, 'wb+') as file:
            file.write(data)
            print(SUCCESSFUL_DOWNLOAD_MESSAGE)
            file.close()
            
def Download_Folder():
    request = 'GET /' + dir + ' HTTP/1.1\r\nHost:' + HOST + '\r\nAccept: text/html,image/gif,image/jpeg,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,audio/mpeg,video/mp4,application/pdf,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation,text/plain\r\nAccept-Language: en-US,en-GB\r\nConnection: keep-alive\r\n\r\n'
    client.sendall(request.encode(FORMAT_WORD))
    
    Check_Response_Type()
    data = b'' 
    CTlen = get_Content_Length(header)
    data += header
    while (len(data) < CTlen + len(header)):
        response = client.recv(1024)
        data += response
        if (not response):
            break
    
    content = data.split(b'\r\n\r\n', 1)[1]
    
    soup = BeautifulSoup(content,features = 'html.parser')
    
    for refs in soup.find_all('a',href = True): 
        tempeof = Path(refs['href']).suffix
        if (tempeof != ''):
            tmpfname = refs['href'] #EX: 01-intro.pdf
            tmpURL = url_in + tmpfname
            tmpHOST = tmpURL.split('//')[1]
            tmpHOST = tmpHOST.split('/')[0] #EX: web.stanford.edu
            
            tmpURL = urlparse(tmpURL)
            tmpdir = tmpURL.path #EX: /class/cs224w/slides/01-intro.pdf
            
            tmprequest = 'GET /' + tmpdir + ' HTTP/1.1\r\nHost:' + tmpHOST + '\r\nAccept: text/html,image/gif,image/jpeg,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,audio/mpeg,video/mp4,application/pdf,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation,text/plain\r\nAccept-Language: en-US,en-GB\r\nConnection: keep-alive\r\n\r\n'
            client.sendall(tmprequest.encode(FORMAT_WORD))
            
            tmpHeader = b''
            tmpHeader = get_Header(tmpHeader)
            tmpdata = b'' #final data of each subfile
            tmpCTlen = get_Content_Length(tmpHeader)
            tmpdata += tmpHeader
            
            while (len(tmpdata) < tmpCTlen + len(tmpHeader)):
                tmpresponse = client.recv(1024)
                if (not tmpresponse):
                    break
                tmpdata += tmpresponse
    
            tmpcontent = tmpdata.split(b'\r\n\r\n', 1)[1]
            
            p = Path(folder + '/')
            p.mkdir(parents=True,exist_ok=True) #make directory
            
            filepath = p / tmpfname #EX: slides/01....
            with filepath.open('wb+') as f:
                f.write(tmpcontent)
            print(SUCCESSFUL_DOWNLOAD_MESSAGE)
   
    client.close()

def init(url_in):                    
    global HOST
    global url
    global dir
    global folder
    global fname 
    global eof 
    global format
    
    HOST = url_in.split('//')[1] #abc.com/index.html
    HOST = HOST.split('/')[0] #abc.com

    url = urlparse(url_in)
    dir = url.path #Ex: /dept/its/support/techtraining/techbriefing-media/Intro_Net_91407.ppt
    folder = os.path.basename(os.path.dirname(dir)) #EX: techbriefing-media
    fname = os.path.basename(dir) #filename ex: Intro_Net_91407.ppt
    eof = Path(fname).suffix #Ex: .ppt

    format = FORMAT_WORD
    ADDR = (HOST, PORT)
    client.connect(ADDR)
    print(SUCCESSFUL_CONNECT_MESSAGE)

def connect_and_Download(url_in):
    init(url_in)
    global isContent_Length
    global isChunked    
    global folder
    global fname

    if (folder != '' and fname == ''):
        Download_Folder()
    else:
        send_Request()  
        Check_Response_Type()

        if (isContent_Length == True and isChunked == False):
            download_Content_Length()
        else:
            download_Chunked()
           
print('Enter the URL or URLs: ')       
url_in = input()

HOST = ''
url = ''
dir = ''
folder = ''
fname = ''
eof = ''
format = ''

PORT = 80
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
isContent_Length = False #flag to check type of response: Content-Length
isChunked = False #flag to check type of response: Transfer-encoding: chunked
header = b'' #header of responses

if (url_in.find(' ') != -1):
    url_list = url_in.split(' ')
    
    for urls in url_list:
        t = threading.Thread(target=connect_and_Download, args=(urls,))
        t.start()
else:
    connect_and_Download(url_in)
                            
