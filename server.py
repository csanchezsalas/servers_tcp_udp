"""
TECNOLÓGICO DE COSTA RICA
CAMPUS TECNOLÓGICO LOCAL SAN CARLOS

CHRISTIAN SÁNCHEZ SALAS

TAREA PROGRAMADA - CURSO REDES - PROTOCOLO IP/(TCP - UDP)

II SEMESTRE
SEPTIEMBRE, 2019"""

import socket
from _thread import *
import threading
import os
# import sys

# THIS HELP HANDLE MULTIPLE CONNECTIONS SO IT CAN BE LOCKED OR UNLOCKED
print_lock = threading.Lock()
# https://wiki.python.org/moin/UdpCommunication
# https://wiki.python.org/moin/TcpCommunication
# thread fuction


# THREAD FUNCTION IN ORDER FOR TCP TO HANDLE MULTIPLE CONNECTIONS
def threaded(name, c):

    # GET PARAMETER -d, -u or -l:
    action_recv = c.recv(1024)
    action = str(action_recv.decode('ascii'))
    if action != '-l':
        c.send(bytes("ok-request", "utf8"))

    # DOWNLOAD
    if action == '-d':

        filename = c.recv(1024)
        filename_parsed = str(filename.decode('ascii'))
        print("filename download request received: ", filename_parsed)
        # list every file from a local repository to check if file exists
        # then get the file size and sends it to the client
        # then start sending file portions
        arr = os.listdir('./files')
        to_do = str(os.path.getsize('.\\files\\' + filename_parsed))
        print("File size: " + to_do)
        c.send(bytes(to_do, "utf8"))
        if arr.count(filename_parsed) > 0:  # this means it exists
            with open('.\\files\\'+filename.decode('ascii'), 'rb') as f:
                bytes_to_send = f.read(1024)
                c.send(bytes_to_send)
                while bytes_to_send != "":
                    bytes_to_send = f.read(1024)
                    c.send(bytes_to_send)
        else:
            c.send("ERR")
        print_lock.release()
        c.close()

    #UPLOAD
    elif action == '-u':
        try:
            file_name = c.recv(1024)
            file_name_parsed = str(file_name.decode('ascii'))
            print("filename upload request received: ", file_name_parsed)
            if file_name_parsed == "ERR":  # if not then it contains the file size
                print("UPLOAD FAILED DUE TO CLIENT ERR\n")
            else:
                c.send(bytes("OK", "utf8"))  # signal to client for it to start uploading
                file_size_bytes = c.recv(1024)
                file_size_parsed = str(file_size_bytes.decode('ascii'))
                file_size = int(file_size_parsed)  # file size

                f = open(".\\files\\" + file_name_parsed, 'wb')
                to_write = c.recv(1024)
                total_recv = len(to_write)
                f.write(to_write)
                while total_recv < file_size:
                    c.send(bytes("UPLOADING", "utf8"))
                    to_write = c.recv(1024)
                    total_recv += len(to_write)
                    f.write(to_write)
                    print("{0:.2f}".format((total_recv / float(file_size)) * 100) + "% Done")
                c.send(bytes("DONE", "utf8"))
                print("UPLOAD FROM CLIENT COMPLETE!\n")

            c.close()
        except error:
            print("UPLOAD FAILED\n")

    # LIST
    elif action == '-l':
        files_list = os.listdir('./files')
        for f in files_list:
            f = '\n'+f
            c.send(bytes(f, "utf8"))

        c.send(bytes("\nDONE", "utf8"))
        # print("HELLO WORLD\n")
    else:
        print("CLIENT CONNECTION ATTEMPT FAILED\n")
    c.close()

    # connection closed


def start_server():

    host = socket.gethostbyname(socket.gethostname())  # REVISAR SI ESTA LINEA DE CÓDIGO OBTIENE BIEN EL LOCALHOST POR AQUELLO DE TENER IP'S VIRTUALES
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'STARTING SERVER ON HOSTNAME: {socket.gethostbyname(host)}')
    s.bind((host, port))
    print("socket bind to port", port)
    s.listen(10)
    print("socket is listening")
    # i = 10
    while True:
        # establish connection with client
        c, addr = s.accept()
        # print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread
        start_new_thread(threaded, ('service_request', c))

    # s.close()


if __name__ == '__main__':
    print("IP FOR SERVER WOULD BE: ", socket.gethostbyname(socket.gethostname()))
    start_server()
