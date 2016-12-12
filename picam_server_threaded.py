import picamera
import picamera_controller
import datetime
import socket
import io
import sys
import ast
import threading
import time
from PIL import Image

class Scope():
    def __init__(self, onentry, onexit):
        self.onentry = onentry
        self.onexit = onexit
    def __enter__(self):
        self.onentry()
        return self.onentry
    def __exit__(self, type, value, traceback):
        self.onexit()

class myThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.camera = picamera.PiCamera()
        params = picamera_controller.load_settings(self.camera)
        picamera_controller.set_params(params, self.camera)
        if 'delay' in params:
            self.delay = params['delay']
        else:
            self.delay = 60
        self.keep_going = True
        self.take_pictures = False
        self.my_lock = threading.Lock()

    def _movement(self):
        res = params['resolution']
        width = 320
        size = width * res[1] / res[0]
        buffer = picamera_controller.take_rgb(self.camera, size)
        ans = movement_rgb(buffer, self.last_image, self.sensitivity)
        self.last_image = buffer
        return ans

    def _take_picture(self):
        buffer = picamera_controller.take_shot(self.camera)
        t = datetime.datetime.now()
        fname = "pictures/pi-{:4d}-{:02d}-{:02d}-{:02d}-{:02d}-{:02d}".format(t.year, t.month, t.day, t.hour, t.minute, t.second)
        with open(fname + ".jpg", 'wb') as out:
            out.write(buffer)
        im = Image.open(fname + ".jpg")
        thumb_width = 320
        size = thumb_width, thumb_width * im.size[1] / im.size[0]
        im.thumbnail(size)
        im.save(fname + ".thumbnail.jpg")
        print("wrote {}".format(fname + ".jpg"))
        
    def run(self):
        while True:
            with Scope(self.my_lock.acquire, self.my_lock.release):
                if not self.keep_going:
                    break
            if self.take_pictures:
                self._take_picture()
            time.sleep(self.delay)

    def stop(self):
        with Scope(self.my_lock.acquire, self.my_lock.release):
            self.keep_going = False

    def process_command(self, cmd):
        if '@' in cmd:
            with Scope(self.my_lock.acquire, self.my_lock.release):
                params = picamera_controller.get_params(self.camera)
                params['delay'] = self.delay
            return "{}".format(params)
        elif '!' in cmd:
            params = picamera_controller.extract_params(cmd[1:])
            with Scope(self.my_lock.acquire, self.my_lock.release):
                picamera_controller.set_params(params, self.camera)
                if 'delay' in params:
                    self.delay = params['delay']
                params = picamera_controller.get_params(self.camera)
                params['delay'] = self.delay
            return "{}".format(params)
        elif '$' in cmd:
            with Scope(self.my_lock.acquire, self.my_lock.release):
                self.take_pictures = True
            return "ok$"
        elif '%' in cmd:
            with Scope(self.my_lock.acquire, self.my_lock.release):
                self.take_pictures = False
            return "ok%"

def get_line(conn):
    buff = ''
    while True:
        tbuff = conn.recv(1024).decode()
        buff += tbuff
        if '\n' in tbuff:
            return buff

def main():
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8000))
    server_socket.listen(0)
    athread = myThread()
    athread.start()
    print("Running")
    try:
        while True:
            try:
                connection = server_socket.accept()[0]
                buff = get_line(connection)
                print(buff)
                if '^' in buff:
                    athread.stop()
                    connection.sendall("ok^\n")
                    connection.close()
                    break
                else:
                    response = athread.process_command(buff)
                    print("response={}".format(response))
                    connection.sendall("{}\n".format(response))
                    connection.close()
            except:
                print("Unexpected error: {}".format(sys.exc_info()[0]))
                connection.sendall("oops\n")
                raise
 
    finally:
        print("finalizing")
        server_socket.close()
        athread.stop()
        athread.join()

if __name__ == "__main__":
    main()
    
