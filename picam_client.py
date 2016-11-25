import socket
import sys
import io
import struct
import datetime
import ast

def get_line(connection):
    buff = ''
    while True:
        tbuff = connection.recv(1024).decode()
        buff += tbuff
        if '\n' in tbuff:
            return buff

def get_picture(socket):
    connection = socket.makefile('rb')
    image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
    if not image_len:
        return
    image_stream = io.BytesIO()
    image_stream.write(connection.read(image_len))
    image_stream.seek(0)
    return image_stream

def request_picture(params, host, port):
    print("params={}".format(params))
    mysocket = socket.socket()
    mysocket.connect((host, port))
    mysocket.send("{}\n".format(params).encode())
    pic = get_picture(mysocket)
    t = datetime.datetime.now()
    fname = "pictures/pi-{}-{}-{}-{}-{}-{}.jpg".format(t.year, t.month, t.day, t.hour, t.minute, t.second)
    with open(fname, 'wb') as out:
        out.write(pic.read())
    mysocket.close()
    print("wrote {}".format(fname))
    pic.seek(0)
    return pic

def set_parameters(params, host, port):
    print("params={}".format(params))
    mysocket = socket.socket()
    mysocket.connect((host, port))
    mysocket.send("!{}\n".format(params).encode())
    params = ast.literal_eval(get_line(mysocket))
    mysocket.close()
    return params

def get_parameters(host, port):
    message = "@\n"
    mysocket = socket.socket()
    mysocket.connect((host, port))
    mysocket.send(message.encode())
    params = ast.literal_eval(get_line(mysocket))
    mysocket.close()
    return params
    
def server_terminate(host, port):
    message = "^\n"
    mysocket = socket.socket()
    mysocket.connect((host, port))
    mysocket.send(message.encode())
    print("{}".format(get_line(mysocket)))
    mysocket.close()
    
