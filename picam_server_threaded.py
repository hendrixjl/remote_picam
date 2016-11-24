#import picamera
#import picamera_controller
import datetime
import socket
import io
import struct
import ast
import threading

class myThread (threading.Thread):
    def __init__(self, delay):
        threading.Thread.__init__(self)
        self.camera = picamera.PiCamera()
        params = picamera_controller.load_settings(self.camera)
        picamera_controller.set_params(params, self.camera)
        self.delay = delay
        self.keep_going = True
        self.take_pictures = False
        self.my_lock = threading.Lock()

    def _take_picture(self):
        buffer = take_shot(self.camera)
        t = datetime.datetime.now()
        fname = "pictures/pi-{}-{}-{}-{}-{}-{}.jpg".format(t.year, t.month, t.day, t.hour, t.minute, t.second)
        with open(fname, 'wb') as out:
            out.write(buffer)
        print("wrote {}".format(fname))
        
    def run(self):
        while True:
            self.my_lock.acquire()
            if not self.keep_going:
                self.my_lock.release()
                break
            self.my_lock.release()
            if self.take_pictures:
                self._take_picture()
            time.sleep(self.delay)

    def stop(self):
        self.my_lock.acquire()
        self.keep_going = False
        self.my_lock.release()

    def process_command(self, cmd):
        if '@' in cmd:
            self.my_lock.acquire()
            params = picamera_controller.get_params(camera)
            self.my_lock.release()
            return params
        elif '!' in cmd:
            params = picamera_controller.extract_params(cmd[1:])
            self.my_lock.acquire()
            picamera_controller.set_params(params, camera)
            params = picamera_controller.get_params(camera)
            self.my_lock.release()
            return "{}".format(params)
        elif '#' in cmd:
            delay = int(cmd[1:])
            self.my_lock.acquire()
            self.delay = delay
            self.my_lock.release()
        elif '$' in cmd:
            self.my_lock.acquire()
            self.take_pictures = True
            self.my_lock.release()
        elif '%' in cmd:
            self.my_lock.acquire()
            self.take_pictures = False
            self.my_lock.release()

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
    athread = myThread(5)
    athread.start()
    print("Running")
    try:
        while True:
            connection = server_socket.accept()[0]
            buff = get_line(connection)
            print(buff)
            if '^' in buff:
                athread.stop()
                break
            else:
                athread.process_command(buff)
    finally:
        server_socket.close()
        athread.join()

if __name__ == "__main__":
    main()
    
