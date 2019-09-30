"""
TECNOLÓGICO DE COSTA RICA
CAMPUS TECNOLÓGICO LOCAL SAN CARLOS

CHRISTIAN SÁNCHEZ SALAS

TAREA PROGRAMADA - CURSO REDES - PROTOCOLO IP/(TCP - UDP)

II SEMESTRE
SEPTIEMBRE, 2019"""

import socket
import threading
from _thread import *
import os

# THIS HELP HANDLE MULTIPLE CONNECTIONS SO IT CAN BE LOCKED OR UNLOCKED
print_lock = threading.Lock()


#AUX METHODS FOR UDP MODE
# LIST FILES
def list_files(conn, addr):

    files_list = os.listdir('./files')
    for f in files_list:
        # f = '\n' + f
        conn.sendto(bytes(f, "utf8"), addr)

    conn.sendto(bytes("DONE", "utf8"), addr)
    print("HELLO WORLD\n")
    # conn.close()

# DOWNLOAD FILES
def download_file(conn, addr):
    conn.sendto(bytes("ok-request", "utf8"), addr)

    filename = conn.recvfrom(1024)
    filename_data = filename[0]
    filename_parsed = str(filename_data.decode('ascii'))

    print("filename download request received: ", filename_parsed)
    # list every file from a local repository to check if file exists
    # then get the file size and sends it to the client
    # then start sending file portions
    arr = os.listdir('./files')
    to_do = str(os.path.getsize('.\\files\\' + filename_parsed))
    print("File size: " + to_do)
    conn.sendto(bytes(to_do, "utf8"), addr)
    if arr.count(filename_parsed) > 0:  # this means it exists
        with open('.\\files\\' + filename_data.decode('ascii'), 'rb') as f:
            bytes_to_send = f.read(1024)
            conn.sendto(bytes_to_send, addr)
            while bytes_to_send != "":
                bytes_to_send = f.read(1024)
                conn.sendto(bytes_to_send, addr)
    else:
        conn.sendto("ERR")
    print_lock.release()
    conn.close()
    return 0

# UPLOAD FILES
def upload_file(conn, addr):
    conn.sendto(bytes("ok-request", "utf8"), addr)
    try:
        file_name = conn.recvfrom(1024)
        file_name_data = file_name[0]
        addr = file_name[1]
        file_name_parsed = str(file_name_data.decode('ascii'))
        print("filename upload request received: ", file_name_parsed)
        if file_name_parsed == "ERR":  # if not then it contains the file size
            print("UPLOAD FAILED DUE TO CLIENT ERR\n")
        else:
            conn.sendto(bytes("OK", "utf8"), addr)  # signal to client for it to start uploading
            file_size_bytes = conn.recvfrom(1024)
            file_size_bytes_data = file_size_bytes[0]
            addr = file_size_bytes[1]
            file_size_parsed = str(file_size_bytes_data.decode('ascii'))
            file_size = int(file_size_parsed)  # file size

            f = open(".\\files\\" + file_name_parsed, 'wb')
            to_write = conn.recvfrom(1024)
            to_write_data = to_write[0]
            total_recv = len(to_write_data)
            f.write(to_write_data)
            while total_recv < file_size:
                conn.sendto(bytes("UPLOADING", "utf8"), addr)
                to_write = conn.recvfrom(1024)
                to_write_data = to_write[0]
                addr = to_write[1]
                total_recv += len(to_write_data)
                f.write(to_write_data)
                print("{0:.2f}".format((total_recv / float(file_size)) * 100) + "% Done")
            conn.sendto(bytes("DONE", "utf8"), addr)
            print("UPLOAD FROM CLIENT COMPLETE!\n")

        conn.close()
    except error:
        print("UPLOAD FAILED\n")

def start_server():
    host = socket.gethostbyname(socket.gethostname())
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f'STARTING SERVER ON HOSTNAME: {socket.gethostbyname(host)}')
    while True:
        # connection with client
        d = s.recvfrom(1024)
        data = d[0]
        addr = d[1]

        if str(data.decode('ascii')) == '-l':
            list_files(s, addr)

        elif str(data.decode('ascii')) == '-d':
            download_file(s, addr)

        else:
            upload_file(s, addr)



if __name__ == '__main__':
    print("IP FOR SERVER WOULD BE: ", socket.gethostbyname(socket.gethostname()))
    start_server()
